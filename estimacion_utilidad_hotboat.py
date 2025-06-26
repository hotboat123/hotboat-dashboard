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
        df_reservas[['ID', 'fecha_trip', 'Customer Email']],
        left_on='id_reserva',
        right_on='ID',
        how='left'
    )
    
    # Renombrar y ordenar columnas
    df_costos = df_costos.rename(columns={
        'fecha_trip': 'fecha',
        'Customer Email': 'email'
    })
    
    df_costos = df_costos[['fecha', 'email', 'id_reserva', 'descripcion', 'monto']]
    df_costos['fecha'] = pd.to_datetime(df_costos['fecha'])
    df_costos = df_costos.sort_values('fecha')
    
    return df_costos

def crear_ingresos(ruta_reservas, ruta_pedidos_extra):
    # Leer reservas
    df_reservas = pd.read_csv(ruta_reservas)
    
    # Crear DataFrame base de ingresos de reservas
    df_ingresos = pd.DataFrame({
        'id_reserva': df_reservas['ID'],
        'descripcion': 'Ingreso por reserva',
        'monto': df_reservas['TOTAL AMOUNT'],
        'fecha_trip': df_reservas['fecha_trip'],
        'email': df_reservas['Customer Email']
    })
    
    
    # Renombrar columnas
    df_ingresos = df_ingresos.rename(columns={
        'fecha_trip': 'fecha',
        'Customer Email': 'email'
    })
    
    # Leer pedidos extra
    df_pedidos = pd.read_csv(ruta_pedidos_extra)
    # Aplicar la función para crear la columna de fecha
    df_pedidos = crear_columna_fecha(df_pedidos)
    
    # Crear DataFrame de ingresos de pedidos extra
    df_ingresos_extra = pd.DataFrame({
        'fecha': df_pedidos['fecha'],
        'email': df_pedidos['email'],
        'descripcion': 'Ingreso por pedido extra',
        'monto': df_pedidos['Total']
    })
    
    # Combinar ingresos
    df_ingresos_combinado = pd.concat([df_ingresos, df_ingresos_extra], ignore_index=True)
    
    # Ordenar columnas y convertir fecha a datetime
    df_ingresos_combinado = df_ingresos_combinado[['fecha', 'email', 'id_reserva', 'descripcion', 'monto']]
    df_ingresos_combinado['fecha'] = pd.to_datetime(df_ingresos_combinado['fecha'])
    df_ingresos_combinado = df_ingresos_combinado.sort_values('fecha')
    
    return df_ingresos_combinado

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