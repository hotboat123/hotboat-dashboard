import pandas as pd

def procesar_fechas_reservas(df):
    """
    Procesa las fechas y horas de un DataFrame de reservas
    
    Args:
        df (pd.DataFrame): DataFrame con las columnas fecha_trip, fecha_creacion_reserva,
                          hora_trip y hora_creacion_reserva
    
    Returns:
        pd.DataFrame: DataFrame con las fechas y horas procesadas
    """
    try:
        # Crear una copia para no modificar el original
        df = df.copy()
        
        # Convertir fechas y horas
        df["fecha_trip"] = pd.to_datetime(df["fecha_trip"], format="%Y-%m-%d")
        df["fecha_creacion_reserva"] = pd.to_datetime(df["fecha_creacion_reserva"], format="%Y-%m-%d")
        df["hora_trip"] = pd.to_datetime(df["hora_trip"], format="%H:%M:%S").dt.time
        df["hora_creacion_reserva"] = pd.to_datetime(df["hora_creacion_reserva"], format="%H:%M:%S").dt.time
        
        return df
    except Exception as e:
        print(f"Error procesando las fechas: {str(e)}")
        return None
    
def procesar_appointments(payments, appointments):
    """
    Procesa las fechas y horas de un DataFrame de reservas
    
    Args:
        df (pd.DataFrame): DataFrame con las columnas fecha_trip, fecha_creacion_reserva,
                          hora_trip y hora_creacion_reserva
    
    Returns:
        pd.DataFrame: DataFrame con las fechas y horas procesadas
    """

    # Cruzar las tablas usando la columna "mail"
    df = pd.merge(payments, appointments, on= 'ID', how='inner')  # "inner" solo deja coincidencias
    
    # 🔥 Eliminar VARIAS columnas (por ejemplo, "edad" y "ciudad")
    df = df.drop(columns=['   ', 'Unnamed: 11',
        'Unnamed: 12', 'Terms &amp; Conditions', ' ', "Customer_y", "Customer Email_y", "SERVICE_y", "Customer Phone Number_y" , "STAFF_y", "Service"])
    
    # Renombrar columnas
    df = df.rename(columns={
        'Customer_x': 'Customer', 
        'Customer Email_x': 'Customer Email', 
        "SERVICE_x": "Service", 
        "Customer Phone Number_x": "Phone Number", 
        "STAFF_x": "STAFF"
    })
    
    # Eliminar filas duplicadas basadas en la columna 'id'
    df = df.drop_duplicates(subset='ID', keep='first')  # 'first' mantiene la primera ocurrencia

    # 🔥 Eliminar el "$" y convertir a número
    df['PAYMENT'] = df['PAYMENT'].replace({'\$': '', '\.': ''}, regex=True).astype(int)
    df['TOTAL AMOUNT'] = df['TOTAL AMOUNT'].replace({'\$': '', '\.': ''}, regex=True).astype(int)
    df['PAID AMOUNT'] = df['PAID AMOUNT'].replace({'\$': '', '\.': ''}, regex=True).astype(int)
    df['DUE AMOUNT'] = df['DUE AMOUNT'].replace({'\$': '', '\.': ''}, regex=True).astype(int)

    # Separar fecha en dos columnas
    df[['fecha_trip', 'hora_trip']] = df['APPOINTMENT DATE'].str.split(' ', expand=True)
    df[['fecha_creacion_reserva', 'hora_creacion_reserva']] = df['CREATED AT'].str.split(' ', expand=True)
    df["fecha_trip"] = pd.to_datetime(df["fecha_trip"], format="%d/%m/%Y")
    df["fecha_creacion_reserva"] = pd.to_datetime(df["fecha_creacion_reserva"], format="%d/%m/%Y")
    df["hora_trip"] = pd.to_datetime(df["hora_trip"], format="%H:%M").dt.time
    df["hora_creacion_reserva"] = pd.to_datetime(df["hora_creacion_reserva"], format="%H:%M").dt.time
    df = df.drop(columns=['APPOINTMENT DATE','START DATE','CREATED AT'])

    # Aplicar la función a la columna 'telefono'
    df['Phone Number_2'] = df['Phone Number'].apply(formatear_telefono)

    return df

    


# Función para asegurar el formato chileno de 11 dígitos
def formatear_telefono(telefono):
    telefono = str(telefono).strip()  # Aseguramos que el teléfono sea un string sin espacios

    # Si el teléfono tiene 8 dígitos (sin prefijo)
    if len(telefono) == 8:
        return "569" + telefono
    elif len(telefono) == 9:
        return "56" + telefono
    # Si el teléfono tiene 11 dígitos y empieza con "569", lo dejamos igual
    elif len(telefono) == 11 and telefono.startswith("569"):
        return telefono
    # Si el teléfono ya tiene 11 dígitos, lo dejamos igual
    elif len(telefono) == 11 and telefono.startswith("569"):
        return telefono
    else:
        return telefono  # Si no cumple ninguna de las condiciones, lo dejamos como está
    
# Función para asegurar el formato chileno de 11 dígitos
def procesar_reservas(df_reservas_original, df_reservas_nuevas):
    """
    Procesa las reservas, combinando las reservas originales con las nuevas si existen,
    o exportando solo las nuevas si no hay originales.
    
    Args:
        df_reservas_original (pd.DataFrame): DataFrame con las reservas originales (puede ser None)
        df_reservas_nuevas (pd.DataFrame): DataFrame con las nuevas reservas
    
    Returns:
        pd.DataFrame: DataFrame con las reservas procesadas
    """
    if df_reservas_original is not None and not df_reservas_original.empty:
        # Asegurar que los nombres de las columnas sean consistentes
        df_reservas_nuevas = df_reservas_nuevas.rename(columns={
            'Service.1': 'Service',
            'SERVICE': 'Service'
        })
        
        # Asegurar que ambos DataFrames tengan las mismas columnas
        columnas_comunes = list(set(df_reservas_original.columns) & set(df_reservas_nuevas.columns))
        df_reservas_original = df_reservas_original[columnas_comunes]
        df_reservas_nuevas = df_reservas_nuevas[columnas_comunes]
        
        # Resetear índices y concatenar
        df_reservas_original = df_reservas_original.reset_index(drop=True)
        df_reservas_nuevas = df_reservas_nuevas.reset_index(drop=True)
        
        # Concatenar DataFrames
        df_concat = pd.concat([df_reservas_original, df_reservas_nuevas], axis=0, ignore_index=True)
        # Eliminar duplicados, manteniendo la primera aparición
        df_final = df_concat.drop_duplicates(subset="ID", keep="first").sort_values(by="fecha_trip")
    else:
        # Si no hay reservas originales, usar solo las nuevas
        df_final = df_reservas_nuevas.reset_index(drop=True).sort_values(by="fecha_trip")
    
    # Procesar fechas y tipos de datos
    df_final["fecha_trip"] = pd.to_datetime(df_final["fecha_trip"], format="%d/%m/%Y")
    df_final["fecha_creacion_reserva"] = pd.to_datetime(df_final["fecha_creacion_reserva"], format="%d/%m/%Y")
    df_final["ID"] = df_final["ID"].astype(int)
    df_final = df_final.sort_values(by="fecha_trip")
    
    return df_final