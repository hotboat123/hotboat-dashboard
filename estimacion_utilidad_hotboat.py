import pandas as pd
import os
from funciones.funciones import crear_columna_fecha
from inputs_modelo import costo_operativo_por_reserva

def crear_costos_operativos(ruta_reservas):
    print(f"Leyendo archivo de reservas desde: {ruta_reservas}")
    
    if not os.path.exists(ruta_reservas):
        raise FileNotFoundError(f"No se encontró el archivo de reservas en: {ruta_reservas}")
    
    df_reservas = pd.read_csv(ruta_reservas)
    print(f"Se leyeron {len(df_reservas)} reservas")
    
    # Crear DataFrame base de costos
    df_costos = pd.DataFrame({
        'id_reserva': df_reservas['ID'],
        'descripcion': 'Costo operativo por reserva',
        'monto': costo_operativo_por_reserva,
    })
    
    # Cruzar con el DataFrame de reservas para obtener fecha y email
    df_costos = df_costos.merge(
        df_reservas[['ID', 'fecha_hora_trip', 'Customer Email']],
        left_on='id_reserva',
        right_on='ID',
        how='left'
    )
    
    # Renombrar y ordenar columnas
    df_costos = df_costos.rename(columns={
        'fecha_hora_trip': 'fecha',
        'Customer Email': 'email'
    })
    
    df_costos = df_costos[['fecha', 'email', 'id_reserva', 'descripcion', 'monto']]
    df_costos['fecha'] = pd.to_datetime(df_costos['fecha'])
    df_costos = df_costos.sort_values('fecha')
    
    return df_costos

def crear_ingresos(ruta_reservas, ruta_pedidos_extra):
    # Leer reservas
    df_reservas = pd.read_csv(ruta_reservas)
    print(f"Leyendo archivo de reservas desde: {ruta_reservas}")
    print(f"Se leyeron {len(df_reservas)} reservas")
    
    # Crear DataFrame base de ingresos de reservas
    df_ingresos = pd.DataFrame({
        'id_reserva': df_reservas['ID'],
        'descripcion': 'Ingreso por reserva',
        'monto': df_reservas['PAID AMOUNT'],
        'fecha_hora_trip': df_reservas['fecha_hora_trip'],
        'email': df_reservas['Customer Email']
    })
    
    # Renombrar columnas
    df_ingresos = df_ingresos.rename(columns={
        'fecha_hora_trip': 'fecha',
        'Customer Email': 'email'
    })
    
    # Leer pedidos extra
    df_pedidos = pd.read_csv(ruta_pedidos_extra)
    print(f"Leyendo archivo de pedidos extra desde: {ruta_pedidos_extra}")
    print(f"Se leyeron {len(df_pedidos)} pedidos extra")
    
    # Aplicar la función para crear la columna de fecha
    df_pedidos = crear_columna_fecha(df_pedidos)
    
    # Preparar datos para el cruce
    # Convertir fechas a datetime para el cruce
    df_ingresos['fecha'] = pd.to_datetime(df_ingresos['fecha'])
    df_pedidos['fecha'] = pd.to_datetime(df_pedidos['fecha'])
    
    # Hacer cruce por fecha y email entre pedidos extra y reservas
    df_pedidos_cruzados = df_pedidos.merge(
        df_ingresos[['fecha', 'email', 'id_reserva']],
        on=['fecha', 'email'],
        how='inner'  # Solo pedidos extra que coincidan con una reserva
    )
    
    print(f"Después del cruce por fecha y email: {len(df_pedidos_cruzados)} pedidos extra coinciden con reservas")
    
    # Crear DataFrame de ingresos de pedidos extra (solo los que coinciden)
    df_ingresos_extra = pd.DataFrame({
        'fecha': df_pedidos_cruzados['fecha'],
        'email': df_pedidos_cruzados['email'],
        'id_reserva': df_pedidos_cruzados['id_reserva'],
        'descripcion': 'Ingreso por pedido extra',
        'monto': df_pedidos_cruzados['Total']
    })
    
    # Combinar ingresos de reservas con pedidos extra que coinciden
    df_ingresos_combinado = pd.concat([df_ingresos, df_ingresos_extra], ignore_index=True)
    
    # Ordenar columnas y convertir fecha a datetime
    df_ingresos_combinado = df_ingresos_combinado[['fecha', 'email', 'id_reserva', 'descripcion', 'monto']]
    df_ingresos_combinado['fecha'] = pd.to_datetime(df_ingresos_combinado['fecha'])
    df_ingresos_combinado = df_ingresos_combinado.sort_values('fecha')
    
    # Crear DataFrame agrupado por fecha y email
    df_ingresos_agrupado = df_ingresos_combinado.groupby(['fecha', 'email']).agg({
        'monto': 'sum',
        'id_reserva': 'first',  # Tomar el primer ID de reserva del grupo
        'descripcion': lambda x: list(x)  # Mantener todas las descripciones para verificar si hay extras
    }).reset_index()
    
    # Crear descripción dinámica basada en si hay extras
    def crear_descripcion_dinamica(descripciones):
        if len(descripciones) > 1 or 'Ingreso por pedido extra' in descripciones:
            return 'Ingreso por reserva + extras'
        else:
            return 'Ingreso por reserva'
    
    df_ingresos_agrupado['descripcion'] = df_ingresos_agrupado['descripcion'].apply(crear_descripcion_dinamica)
    
    # Reordenar columnas para mantener consistencia
    df_ingresos_agrupado = df_ingresos_agrupado[['fecha', 'email', 'id_reserva', 'descripcion', 'monto']]
    
    print(f"Total de ingresos (reservas + pedidos extra coincidentes): {len(df_ingresos_combinado)}")
    print(f"Total de ingresos agrupados por fecha y email: {len(df_ingresos_agrupado)}")
    
    return df_ingresos_agrupado

def main():

    ruta_reservas = 'archivos_output/reservas_HotBoat.csv'
    ruta_pedidos_extra = 'archivos_input/Archivos input reservas/HotBoat - Pedidos Extras.csv'
    ruta_salida_costos = 'archivos_output/costos_operativos.csv'
    ruta_salida_ingresos = 'archivos_output/ingresos_operativos.csv'
    
    # Procesar costos
    df_costos = crear_costos_operativos(ruta_reservas)
    df_costos.to_csv(ruta_salida_costos, index=False)
    
    # Procesar ingresos
    df_ingresos = crear_ingresos(ruta_reservas, ruta_pedidos_extra)
    df_ingresos.to_csv(ruta_salida_ingresos, index=False)
    
    print("Procesamiento completado exitosamente")
    


if __name__ == "__main__":
    main()