import os
os.environ['MPLBACKEND'] = 'Agg'  # Forzar backend Agg antes de importar matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from datetime import datetime
import locale
import numpy as np
import matplotlib.dates as mdates
import traceback
import plotly.graph_objects as go
import plotly.express as px

# Crear directorio para gráficos si no existe
GRAFICOS_DIR = 'graficos'
if not os.path.exists(GRAFICOS_DIR):
    os.makedirs(GRAFICOS_DIR)

# Configurar el estilo de los gráficos
plt.style.use('seaborn')
sns.set_palette("husl")

# Configurar locale para formato de moneda
try:
    locale.setlocale(locale.LC_ALL, 'es_CL.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'es-CL')
    except:
        print("No se pudo configurar el locale para Chile, usando configuración por defecto")

def formato_moneda(valor):
    """Formatea un número como moneda chilena"""
    return locale.currency(valor, grouping=True)

def cargar_datos():
    """Carga los DataFrames de gastos y abonos"""
    try:
        df_gastos = pd.read_csv("archivos_output/gastos hotboat.csv")
        df_abonos = pd.read_csv("archivos_output/abonos hotboat.csv")
        
        # Convertir fechas - intentar ambos formatos posibles
        def convertir_fecha(fecha):
            try:
                return pd.to_datetime(fecha, format='%d/%m/%Y')
            except:
                return pd.to_datetime(fecha)
        
        df_gastos['Fecha'] = df_gastos['Fecha'].apply(convertir_fecha)
        df_abonos['Fecha'] = df_abonos['Fecha'].apply(convertir_fecha)
        
        return df_gastos, df_abonos
    except Exception as e:
        print(f"Error cargando los datos: {str(e)}")
        return None, None

def procesar_fechas_reservas(df):
    """Procesa las fechas y horas de un DataFrame de reservas"""
    try:
        df = df.copy()
        df["fecha_trip"] = pd.to_datetime(df["fecha_trip"])
        df["fecha_creacion_reserva"] = pd.to_datetime(df["fecha_creacion_reserva"])
        return df
    except Exception as e:
        print(f"Error procesando fechas: {e}")
        return None

def grafico_gastos_por_categoria(df_gastos):
    """Genera un gráfico de torta de gastos por categoría"""
    plt.figure(figsize=(12, 8))
    
    # Usar valores absolutos para los montos
    gastos_categoria = df_gastos.groupby('Categoría')['Monto'].sum().abs()
    
    # Crear etiquetas con el signo correcto
    labels = []
    for cat, monto in df_gastos.groupby('Categoría')['Monto'].sum().items():
        signo = '-' if monto < 0 else '+'
        monto_abs = abs(monto)
        labels.append(f"{cat}\n{signo}{formato_moneda(monto_abs)}")
    
    # Crear gráfico de torta
    plt.pie(gastos_categoria, labels=labels, autopct='%1.1f%%')
    plt.title('Distribución de Gastos por Categoría')
    plt.axis('equal')
    plt.savefig(os.path.join(GRAFICOS_DIR, 'gastos_por_categoria.png'), bbox_inches='tight')
    plt.close()

def grafico_tendencia_temporal(df_gastos, df_abonos):
    """Genera un gráfico de línea mostrando la tendencia de gastos y abonos en el tiempo"""
    plt.figure(figsize=(15, 8))
    
    # Agrupar por mes
    gastos_mensuales = df_gastos.groupby(df_gastos['Fecha'].dt.to_period('M'))['Monto'].sum()
    abonos_mensuales = df_abonos.groupby(df_abonos['Fecha'].dt.to_period('M'))['Monto'].sum()
    
    # Convertir períodos a fechas para el gráfico
    gastos_mensuales.index = gastos_mensuales.index.astype(str)
    abonos_mensuales.index = abonos_mensuales.index.astype(str)
    
    # Usar valores absolutos y añadir signo en la leyenda
    plt.plot(gastos_mensuales.index, gastos_mensuales.abs().values, marker='o', label='Gastos (-)')
    plt.plot(abonos_mensuales.index, abonos_mensuales.values, marker='o', label='Abonos (+)')
    
    plt.title('Tendencia de Gastos y Abonos Mensuales')
    plt.xlabel('Mes')
    plt.ylabel('Monto (CLP)')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(GRAFICOS_DIR, 'tendencia_temporal.png'))
    plt.close()

def grafico_barras_categorias_mensual(df_gastos):
    """Genera un gráfico de barras apiladas mostrando gastos por categoría por mes"""
    plt.figure(figsize=(15, 8))
    
    # Crear pivot table para el gráfico usando valores absolutos
    pivot = pd.pivot_table(
        df_gastos,
        values='Monto',
        index=df_gastos['Fecha'].dt.to_period('M'),
        columns='Categoría',
        aggfunc=lambda x: abs(x.sum()),  # Usar valores absolutos
        fill_value=0
    )
    
    # Convertir períodos a strings para el gráfico
    pivot.index = pivot.index.astype(str)
    
    # Crear gráfico de barras
    ax = pivot.plot(kind='bar', stacked=True)
    
    # Añadir etiquetas con signos
    handles = ax.get_legend().legendHandles
    labels = [f"{cat} (-)" for cat in pivot.columns]
    ax.legend(handles, labels, title='Categoría', bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.title('Gastos Mensuales por Categoría')
    plt.xlabel('Mes')
    plt.ylabel('Monto (CLP)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(GRAFICOS_DIR, 'gastos_categoria_mensual.png'), bbox_inches='tight')
    plt.close()

def generar_resumen_estadistico(df_gastos, df_abonos):
    """Genera un resumen estadístico de gastos y abonos"""
    resumen = {
        'Total Gastos': df_gastos['Monto'].sum(),
        'Total Abonos': df_abonos['Monto'].sum(),
        'Balance': df_abonos['Monto'].sum() - df_gastos['Monto'].sum(),
        'Promedio Gastos Mensual': df_gastos.groupby(df_gastos['Fecha'].dt.to_period('M'))['Monto'].sum().mean(),
        'Promedio Abonos Mensual': df_abonos.groupby(df_abonos['Fecha'].dt.to_period('M'))['Monto'].sum().mean(),
        'Mes con Más Gastos': df_gastos.groupby(df_gastos['Fecha'].dt.to_period('M'))['Monto'].sum().idxmax(),
        'Mes con Más Abonos': df_abonos.groupby(df_abonos['Fecha'].dt.to_period('M'))['Monto'].sum().idxmax()
    }
    
    # Crear DataFrame con el resumen
    df_resumen = pd.DataFrame(list(resumen.items()), columns=['Métrica', 'Valor'])
    df_resumen.to_csv(os.path.join(GRAFICOS_DIR, 'resumen_estadistico.csv'), index=False)
    
    return resumen

def grafico_balance_acumulado(df_gastos, df_abonos):
    """Genera un gráfico de balance acumulado en el tiempo"""
    plt.figure(figsize=(15, 8))
    
    # Crear series diarias
    gastos_diarios = df_gastos.groupby('Fecha')['Monto'].sum()
    abonos_diarios = df_abonos.groupby('Fecha')['Monto'].sum()
    
    # Crear índice de fechas completo
    fecha_inicio = min(gastos_diarios.index.min(), abonos_diarios.index.min())
    fecha_fin = max(gastos_diarios.index.max(), abonos_diarios.index.max())
    fechas_completas = pd.date_range(start=fecha_inicio, end=fecha_fin, freq='D')
    
    # Rellenar fechas faltantes con 0
    gastos_diarios = gastos_diarios.reindex(fechas_completas, fill_value=0)
    abonos_diarios = abonos_diarios.reindex(fechas_completas, fill_value=0)
    
    # Calcular balance acumulado
    balance_acumulado = (abonos_diarios - gastos_diarios).cumsum()
    
    # Graficar
    plt.plot(fechas_completas, balance_acumulado, 'b-', linewidth=2)
    plt.fill_between(fechas_completas, balance_acumulado, where=balance_acumulado >= 0, 
                    color='green', alpha=0.3)
    plt.fill_between(fechas_completas, balance_acumulado, where=balance_acumulado < 0, 
                    color='red', alpha=0.3)
    
    plt.title('Balance Acumulado en el Tiempo')
    plt.xlabel('Fecha')
    plt.ylabel('Balance (CLP)')
    plt.grid(True, alpha=0.3)
    
    # Formatear eje y con moneda
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: formato_moneda(x)))
    
    plt.tight_layout()
    plt.savefig(os.path.join(GRAFICOS_DIR, 'balance_acumulado.png'))
    plt.close()

def grafico_ingresos_vs_gastos_mensual(df_gastos, df_abonos):
    """Genera un gráfico de barras comparando ingresos vs gastos por mes"""
    plt.figure(figsize=(15, 8))
    
    # Agrupar por mes
    gastos_mensuales = df_gastos.groupby(df_gastos['Fecha'].dt.to_period('M'))['Monto'].sum().abs()
    abonos_mensuales = df_abonos.groupby(df_abonos['Fecha'].dt.to_period('M'))['Monto'].sum()
    
    # Crear DataFrame para el gráfico
    df_comparacion = pd.DataFrame({
        'Gastos': gastos_mensuales,
        'Ingresos': abonos_mensuales
    })
    
    # Convertir índice a string para el gráfico
    df_comparacion.index = df_comparacion.index.astype(str)
    
    # Graficar barras
    ax = df_comparacion.plot(kind='bar', width=0.8)
    
    plt.title('Ingresos vs Gastos Mensuales')
    plt.xlabel('Mes')
    plt.ylabel('Monto (CLP)')
    plt.grid(True, alpha=0.3)
    plt.legend(['Gastos', 'Ingresos'])
    
    # Formatear eje y con moneda
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: formato_moneda(x)))
    
    # Rotar etiquetas del eje x
    plt.xticks(rotation=45)
    
    # Agregar valores sobre las barras
    for container in ax.containers:
        labels = [formato_moneda(v) for v in container.datavalues]
        ax.bar_label(container, labels=labels, rotation=0)
    
    plt.tight_layout()
    plt.savefig(os.path.join(GRAFICOS_DIR, 'ingresos_vs_gastos_mensual.png'))
    plt.close()

def grafico_flujo_caja_neto(df_gastos, df_abonos):
    """Genera un gráfico de líneas mostrando el flujo de caja neto mensual"""
    plt.figure(figsize=(15, 8))
    
    # Calcular flujo neto mensual
    gastos_mensuales = df_gastos.groupby(df_gastos['Fecha'].dt.to_period('M'))['Monto'].sum()
    abonos_mensuales = df_abonos.groupby(df_abonos['Fecha'].dt.to_period('M'))['Monto'].sum()
    flujo_neto = abonos_mensuales - gastos_mensuales
    
    # Convertir índice a string
    flujo_neto.index = flujo_neto.index.astype(str)
    
    # Crear gráfico
    plt.plot(range(len(flujo_neto)), flujo_neto.values, 'b-o', linewidth=2)
    
    # Agregar área sombreada
    plt.fill_between(range(len(flujo_neto)), flujo_neto.values, 
                    where=flujo_neto.values >= 0, color='green', alpha=0.3)
    plt.fill_between(range(len(flujo_neto)), flujo_neto.values, 
                    where=flujo_neto.values < 0, color='red', alpha=0.3)
    
    plt.title('Flujo de Caja Neto Mensual')
    plt.xlabel('Mes')
    plt.ylabel('Flujo Neto (CLP)')
    plt.grid(True, alpha=0.3)
    
    # Configurar eje x
    plt.xticks(range(len(flujo_neto)), flujo_neto.index, rotation=45)
    
    # Formatear eje y con moneda
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: formato_moneda(x)))
    
    # Agregar línea de cero
    plt.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    
    # Agregar valores sobre los puntos
    for i, v in enumerate(flujo_neto.values):
        plt.text(i, v, formato_moneda(v), ha='center', va='bottom' if v >= 0 else 'top')
    
    plt.tight_layout()
    plt.savefig(os.path.join(GRAFICOS_DIR, 'flujo_caja_neto.png'))
    plt.close()

def grafico_heatmap_movimientos(df_gastos, df_abonos):
    """Genera un heatmap que muestra los días con mayor movimiento"""
    plt.figure(figsize=(15, 8))
    
    # Combinar gastos y abonos
    df_gastos['Tipo'] = 'Gasto'
    df_abonos['Tipo'] = 'Abono'
    df_combinado = pd.concat([df_gastos, df_abonos])
    
    # Crear matriz para el heatmap
    df_combinado['Día'] = df_combinado['Fecha'].dt.day
    df_combinado['Mes'] = df_combinado['Fecha'].dt.month
    
    # Contar movimientos por día
    movimientos = df_combinado.groupby(['Mes', 'Día']).size().unstack(fill_value=0)
    
    # Crear heatmap
    sns.heatmap(movimientos, cmap='YlOrRd', annot=True, fmt='d', cbar_kws={'label': 'Cantidad de Movimientos'})
    
    plt.title('Heatmap de Movimientos por Día del Mes')
    plt.xlabel('Día del Mes')
    plt.ylabel('Mes')
    
    plt.tight_layout()
    plt.savefig(os.path.join(GRAFICOS_DIR, 'heatmap_movimientos.png'))
    plt.close()

def grafico_reservas_por_dia(df):
    """Genera gráfico de reservas por día"""
    try:
        # Crear directorio si no existe
        if not os.path.exists('graficos'):
            os.makedirs('graficos')
            
        # Contar reservas por día
        reservas_diarias = df.groupby('fecha_trip').size().reset_index(name='cantidad')
        
        # Crear gráfico
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=reservas_diarias['fecha_trip'],
            y=reservas_diarias['cantidad'],
            text=reservas_diarias['cantidad'],
            textposition='auto',
        ))
        
        # Configurar diseño
        fig.update_layout(
            title='Reservas por Día',
            xaxis_title='Fecha',
            yaxis_title='Número de Reservas',
            xaxis_tickformat='%d',
            showlegend=False,
            height=600,
            width=1200
        )
        
        # Guardar gráfico
        fig.write_html('graficos/reservas_por_dia.html')
        print("Gráfico por día generado exitosamente")
        
    except Exception as e:
        print(f"Error generando gráfico por día: {e}")
        import traceback
        print(traceback.format_exc())

def grafico_reservas_por_mes(df):
    """Genera gráfico de reservas por mes"""
    try:
        # Contar reservas por mes
        df['mes'] = df['fecha_trip'].dt.strftime('%Y-%m')
        reservas_mensuales = df.groupby('mes').size().reset_index(name='cantidad')
        
        # Crear gráfico
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=reservas_mensuales['mes'],
            y=reservas_mensuales['cantidad'],
            text=reservas_mensuales['cantidad'],
            textposition='auto',
        ))
        
        # Configurar diseño
        fig.update_layout(
            title='Reservas por Mes',
            xaxis_title='Mes',
            yaxis_title='Número de Reservas',
            showlegend=False,
            height=600,
            width=1200
        )
        
        # Guardar gráfico
        fig.write_html('graficos/reservas_por_mes.html')
        print("Gráfico por mes generado exitosamente")
        
    except Exception as e:
        print(f"Error generando gráfico por mes: {e}")
        import traceback
        print(traceback.format_exc())

def grafico_horas_populares(df_reservas):
    """Genera un gráfico de barras mostrando las horas más populares para los trips"""
    plt.figure(figsize=(15, 8))
    
    # Convertir hora_trip a string para poder agrupar
    horas = [str(hora) for hora in df_reservas['hora_trip']]
    conteo_horas = pd.Series(horas).value_counts().sort_index()
    
    # Crear gráfico de barras
    ax = conteo_horas.plot(kind='bar', color='lightgreen')
    
    plt.title('Horarios Más Populares para Trips')
    plt.xlabel('Hora del Día')
    plt.ylabel('Número de Reservas')
    plt.grid(True, alpha=0.3)
    
    # Rotar etiquetas del eje x
    plt.xticks(rotation=45)
    
    # Agregar valores sobre las barras
    for i, v in enumerate(conteo_horas):
        ax.text(i, v, str(v), ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(os.path.join(GRAFICOS_DIR, 'horas_populares.png'))
    plt.close()

def grafico_tiempo_anticipacion(df_reservas):
    """Genera un histograma mostrando con cuánta anticipación se hacen las reservas"""
    plt.figure(figsize=(15, 8))
    
    # Calcular días de anticipación
    anticipacion = (df_reservas['fecha_trip'] - df_reservas['fecha_creacion_reserva']).dt.days
    
    # Crear histograma
    plt.hist(anticipacion, bins=30, color='lightcoral', edgecolor='black')
    
    plt.title('Distribución de Días de Anticipación en Reservas')
    plt.xlabel('Días de Anticipación')
    plt.ylabel('Número de Reservas')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(GRAFICOS_DIR, 'anticipacion_reservas.png'))
    plt.close()

def graficar_reservas_por_dia_mes(df_reservas):
    """
    Genera un gráfico de líneas mostrando las reservas por día, separadas por mes.
    
    Args:
        df_reservas (pd.DataFrame): DataFrame con las reservas. Debe contener una columna 'fecha'
                                  en formato datetime.
    """
    plt.figure(figsize=(15, 8))
    
    # Extraer el mes y día de la fecha
    df_reservas['mes_trip'] = df_reservas['fecha_trip'].dt.month
    df_reservas['dia_trip'] = df_reservas['fecha_trip'].dt.day
    
    # Contar reservas por día y mes
    reservas_por_dia = df_reservas.groupby(['mes_trip', 'dia_trip']).size().reset_index(name='cantidad')
    
    # Crear el gráfico
    sns.lineplot(data=reservas_por_dia, x='dia_trip', y='cantidad', hue='mes_trip')
    
    # Personalizar el gráfico
    plt.title('Reservas por día separadas por mes')
    plt.xlabel('Día del mes')
    plt.ylabel('Cantidad de reservas')
    plt.legend(title='Mes')
    plt.grid(True, alpha=0.3)
    
    # Guardar el gráfico
    plt.savefig(os.path.join(GRAFICOS_DIR, 'reservas_por_dia_mes.png'), bbox_inches='tight')
    plt.close()

def main():
    try:
        print("Leyendo archivo de reservas...")
        df = pd.read_csv("archivos_output/reservas_HotBoat.csv")
        
        print("Procesando fechas...")
        df = procesar_fechas_reservas(df)
        if df is None:
            return
        
        print("Generando gráficos...")
        grafico_reservas_por_dia(df)
        grafico_reservas_por_mes(df)
        print("Proceso completado")
        
    except Exception as e:
        print(f"Error en el proceso principal: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    main() 