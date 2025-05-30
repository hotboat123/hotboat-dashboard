import pandas as pd


def ver_si_es_nacional_facturado(ruta_archivo):    
    # Leer el archivo de Excel y buscar la fila que contiene 'Categoría'
    df = pd.read_excel(ruta_archivo, sheet_name='Hoja1', header=None)  # Leemos sin encabezado
    # Encontrar la fila donde está la celda 'Categoría'
    categoria_fila = df[df.apply(lambda x: x.astype(str).str.contains('Categoría', case=False).any(), axis=1)].index[0]
    df_final = pd.read_excel(ruta_archivo, sheet_name='Hoja1', skiprows=categoria_fila, header=0)
    if "Monto Moneda Origen" in df_final.columns:
      return False
    return True

def ver_si_es_nacional_no_facturado(ruta_archivo):    
    # Leer el archivo de Excel y buscar la fila que contiene 'Categoría'
    df = pd.read_excel(ruta_archivo, sheet_name='Saldo y Mov No Facturado', header=None)  # Leemos sin encabezado
    # Encontrar la fila donde está la celda 'Categoría'
    descripcion_fila = df[df.apply(lambda x: x.astype(str).str.contains('Descripción', case=False).any(), axis=1)].index[0]
    df_final = pd.read_excel(ruta_archivo, sheet_name='Saldo y Mov No Facturado', skiprows=descripcion_fila, header=0)
    if "Monto (USD)" in df_final.columns:
      return False
    return True

# Función para leer el archivo Mov facturado
def leer_excel_mov_facturados_nacional(ruta_archivo):
    # Leer el archivo de Excel y buscar la fila que contiene 'Categoría'
    df = pd.read_excel(ruta_archivo, sheet_name='Hoja1', header=None)  # Leemos sin encabezado
    
    # Encontrar la fila donde está la celda 'Categoría'
    categoria_fila = df[df.apply(lambda x: x.astype(str).str.contains('Categoría', case=False).any(), axis=1)].index[0]

    # Leer el archivo nuevamente desde la fila que contiene 'Categoría', usando esa fila como header
    df_final = pd.read_excel(ruta_archivo, sheet_name='Hoja1', skiprows=categoria_fila, header=0)
    df_final["Monto"] = df_final["Monto ($)"]
    df_final=df_final[["Fecha","Descripción","Monto","Cuotas","Categoría"]]
  
    return df_final

# Función para leer el archivo Mov No facturado
def leer_excel_mov_no_facturados_nacional(ruta_archivo):
    # Leer el archivo de Excel y buscar la fila que contiene 'Categoría'
    df = pd.read_excel(ruta_archivo, sheet_name='Saldo y Mov No Facturado', header=None)  # Leemos sin encabezado
    
    # Encontrar la fila donde está la celda 'Categoría'
    descripcion_fila = df[df.apply(lambda x: x.astype(str).str.contains('Descripción', case=False).any(), axis=1)].index[0]

    # Leer el archivo nuevamente desde la fila que contiene 'Categoría', usando esa fila como header
    df_final = pd.read_excel(ruta_archivo, sheet_name='Saldo y Mov No Facturado', skiprows=descripcion_fila, header=0)
    df_final["Monto"] = df_final["Unnamed: 10"]
    df_final=df_final[["Fecha","Descripción","Cuotas","Monto", "Ciudad"]]
  
    return df_final


def leer_excel_banco_estado(ruta_archivo, año_para_fecha_banco_estado):
    # Leer el archivo de Excel y buscar la fila que contiene 'Categoría'
    df = pd.read_excel(ruta_archivo, sheet_name="Movimientos", header=None)  # Leemos sin encabezado
    
    # Encontrar la fila donde está la celda 'Categoría'
    descripcion_fila = df[df.apply(lambda x: x.astype(str).str.contains('Descripción', case=False).any(), axis=1)].index[0]

    # Leer el archivo nuevamente desde la fila que contiene 'Categoría', usando esa fila como header
    df_final = pd.read_excel(ruta_archivo, sheet_name="Movimientos", skiprows=descripcion_fila
                             , header=0)
    # Agregar el año "2025" a cada fecha
    df_final['Fecha'] = df_final['Fecha'] + '/' + año_para_fecha_banco_estado

    # Crear copias explícitas para evitar SettingWithCopyWarning
    df_cargos = df_final[df_final['Cheques / Cargos'] > 0].copy()
    df_abonos = df_final[df_final['Cheques / Cargos'] == 0].copy()
    
    # Asignar valores usando loc para evitar advertencias
    df_abonos.loc[:, 'Monto'] = df_abonos['Depósitos / Abonos']
    df_abonos.loc[:, 'Monto'] = df_abonos['Monto'].replace({'\$': '', '\.': ''}, regex=True).astype(int)
    df_abonos = df_abonos[["Fecha","Descripción","Monto"]]
    
    df_cargos.loc[:, 'Monto'] = df_cargos['Cheques / Cargos']
    df_cargos = df_cargos[["Fecha","Descripción","Monto"]]
  
    return df_cargos, df_abonos
    
# Función para leer el archivo Mov No facturado
def leer_excel_mercado_pago(ruta_archivo, año_para_fecha):
    """
    Lee un archivo Excel de Mercado Pago y procesa los datos según los requerimientos.
    
    Args:
        ruta_archivo (str): Ruta al archivo Excel de Mercado Pago
        año_para_fecha (str): Año a agregar a la fecha (ej: "2025")
        
    Returns:
        tuple: (df_pagos, df_reembolsos) donde:
            - df_pagos: DataFrame con los pagos aprobados
            - df_reembolsos: DataFrame con los pagos reembolsados
    """
    # Leer el archivo Excel sin encabezado primero
    df = pd.read_excel(ruta_archivo, header=None)
    
    # Encontrar la fila que contiene 'Número de operación'
    inicio_tabla = df[df.astype(str).apply(lambda x: x.str.contains('Número de operación', case=False)).any(axis=1)].index[0]
    
    # Leer el Excel nuevamente usando la fila de 'Número de operación' como encabezado
    df = pd.read_excel(ruta_archivo, skiprows=inicio_tabla, header=0)
    
    # Convertir la fecha al formato correcto y agregar el año
    def convertir_fecha(fecha_str):
        try:
            # Remover 'hs' y espacios extra
            fecha_str = fecha_str.replace(' hs', '').strip()
            
            # Separar la fecha en partes
            partes = fecha_str.split(' ')
            
            # Si tiene 3 partes, es formato corto (día mes hora)
            # Si tiene 4 partes, es formato largo (día mes año hora)
            if len(partes) == 3:
                dia, mes, hora = partes
                año = año_para_fecha # O el año que necesites
            elif len(partes) == 4:
                dia, mes, año, hora = partes
            else:
                raise ValueError(f"Formato de fecha inesperado: {fecha_str}")
                
            # Diccionario para convertir nombres de meses en español
            meses = {
                'ene': '01', 'feb': '02', 'mar': '03', 'abr': '04',
                'may': '05', 'jun': '06', 'jul': '07', 'ago': '08',
                'sep': '09', 'oct': '10', 'nov': '11', 'dic': '12'
            }
            
            # Convertir el mes a número
            mes = meses[mes.lower()]
            
            # Formatear la fecha completa
            fecha_completa = f"{dia.zfill(2)}/{mes}/{año} {hora}"
            
            # Convertir a datetime
            return pd.to_datetime(fecha_completa, format='%d/%m/%Y %H:%M')
        except Exception as e:
            print(f"Error al convertir fecha '{fecha_str}': {str(e)}")
            return None
    
    # Aplicar la conversión de fecha
    df['fecha'] = df['Fecha de la compra'].apply(convertir_fecha)
    
    # Crear columna de descripción con valor fijo
    df['descripcion'] = 'mercadopago'
    
    # Seleccionar y renombrar las columnas necesarias
    columnas_requeridas = {
        'fecha': 'Fecha',
        'descripcion': 'Descripción',
        'Total a recibir': 'Monto',
        'Herramienta de cobro': 'Herramienta de cobro',
        'Medio de pago': 'Medio de pago'
    }
    
    # Crear DataFrame de pagos aprobados
    df_pagos = df[df['Estado'] == 'Aprobado'].copy()
    df_pagos = df_pagos[columnas_requeridas.keys()].rename(columns=columnas_requeridas)
    
    # Crear DataFrame de reembolsos
    df_reembolsos = df[df['Estado'] == 'Reembolsado'].copy()
    df_reembolsos = df_reembolsos[columnas_requeridas.keys()].rename(columns=columnas_requeridas)
    
    # Asegurar que el Monto sea numérico
    df_pagos['Monto'] = df_pagos['Monto'].str.replace('$', '').str.replace('.', '')
    df_reembolsos['Monto'] = df_reembolsos['Monto'].str.replace('$', '').str.replace('.', '')
    df_pagos['Monto'] = pd.to_numeric(df_pagos['Monto'], errors='coerce')
    df_reembolsos['Monto'] = pd.to_numeric(df_reembolsos['Monto'], errors='coerce') 

    # Eliminar duplicados y ordenar por fecha
    df_pagos = df_pagos.drop_duplicates(subset=['Fecha', 'Monto', 'Medio de pago'], keep='first')
    df_reembolsos = df_reembolsos.drop_duplicates(subset=['Fecha', 'Monto', 'Medio de pago'], keep='first')
    
    # Ordenar por fecha
    df_pagos = df_pagos.sort_values('Fecha')
    df_reembolsos = df_reembolsos.sort_values('Fecha')
    
    return df_pagos, df_reembolsos


def leer_excel_mov_facturados_internacional(ruta_archivo, valor_aproximado_dolar):
    # Leer el archivo de Excel y buscar la fila que contiene 'Categoría'
    df = pd.read_excel(ruta_archivo, sheet_name='Hoja1', header=None)  # Leemos sin encabezado
    
    # Encontrar la fila donde está la celda 'Categoría'
    categoria_fila = df[df.apply(lambda x: x.astype(str).str.contains('Categoría', case=False).any(), axis=1)].index[0]

    # Leer el archivo nuevamente desde la fila que contiene 'Categoría', usando esa fila como header
    df_final = pd.read_excel(ruta_archivo, sheet_name='Hoja1', skiprows=categoria_fila, header=0)
    df_final['Monto'] = df_final['Monto (USD)'] * valor_aproximado_dolar
    df_final=df_final[['Fecha', 'Descripción', 'Categoría', 'País', 'Monto', 'Monto (USD)']]
    return df_final


def leer_excel_mov_no_facturados_internacional(ruta_archivo, valor_aproximado_dolar):
    # Leer el archivo de Excel y buscar la fila que contiene 'Categoría'
    df = pd.read_excel(ruta_archivo, sheet_name='Saldo y Mov No Facturado', header=None)  # Leemos sin encabezado
    
    # Encontrar la fila donde está la celda 'Categoría'
    descripcion_fila = df[df.apply(lambda x: x.astype(str).str.contains('Descripción', case=False).any(), axis=1)].index[0]

    # Leer el archivo nuevamente desde la fila que contiene 'Categoría', usando esa fila como header
    df_final = pd.read_excel(ruta_archivo, sheet_name='Saldo y Mov No Facturado', skiprows=descripcion_fila, header=0)
    df_final=df_final[['Fecha', 'Descripción', 'País', 'Monto (USD)']]
    df_final['Monto'] = df_final['Monto (USD)'] * valor_aproximado_dolar
    return df_final

def leer_pdf(ruta_archivo):
    """
    Lee y procesa un archivo PDF de estado de cuenta, extrayendo transacciones y categorizándolas.
    
    Args:
        ruta_archivo (str): Ruta al archivo PDF a procesar
        
    Returns:
        pd.DataFrame: DataFrame con las transacciones procesadas y categorizadas
    """
    import pdfplumber
    import re
    from typing import Dict, List
    
    # Definir las categorías y sus patrones de búsqueda
    CATEGORIAS = {
        'Marketing': ['FACEBK', 'META', 'INSTAGRAM'],
        'Comisiones': [],  # Se maneja por sección
        'Compras': []      # Categoría por defecto
    }
    
    # Patrones de líneas a ignorar
    PATRONES_IGNORAR = [
        "MONTO FACTURADO",
        "TOTAL OPERACIONES",
        "MOVIMIENTOS TARJETA",
        "TOTAL"
    ]
    
    def categorizar_transaccion(linea: str, en_seccion_comisiones: bool) -> str:
        """Determina la categoría de una transacción basada en su descripción."""
        if en_seccion_comisiones:
            return "Comisiones"
        
        # Buscar en patrones de categorías específicas
        for categoria, patrones in CATEGORIAS.items():
            if any(patron in linea.upper() for patron in patrones):
                return categoria
        
        return "Compras"
    
    def extraer_monto(linea: str) -> str:
        """Extrae y limpia el monto de una línea."""
        monto_match = re.search(r'\$?[\d,.]+$', linea)
        if monto_match:
            return monto_match.group(0).replace('$', '').replace('.', '').replace(',', '')
        return ""
    
    def procesar_linea(linea: str, en_seccion_comisiones: bool) -> Dict:
        """Procesa una línea y extrae la información relevante."""
        match = re.search(r'(?:(\w+)\s*)?(\d{2}/\d{2}/\d{2})', linea)
        if not match:
            return None
            
        partes = linea.split()
        if len(partes) < 2:
            return None
            
        lugar_operacion = match.group(1) if match.group(1) else "MP"
        fecha = match.group(2)
        
        # Extraer monto
        monto = extraer_monto(linea)
        if not monto or not monto.isdigit():
            return None
            
        # Extraer descripción
        idx_fecha = linea.find(fecha) + len(fecha)
        idx_monto = linea.rfind(monto)
        descripcion = linea[idx_fecha:idx_monto].strip()
        descripcion = re.sub(r'^\W+', '', descripcion)
        descripcion = re.sub(r'\s+', ' ', descripcion)
        
        if not descripcion:
            return None
            
        return {
            'Lugar de Operación': lugar_operacion,
            'Fecha': fecha,
            'Descripción': descripcion,
            'Monto': monto,
            'Categoría': categorizar_transaccion(linea, en_seccion_comisiones)
        }
    
    try:
        # Leer el PDF
        with pdfplumber.open(ruta_archivo) as pdf:
            texto_completo = "\n".join(pagina.extract_text() for pagina in pdf.pages)
        
        # Procesar el texto
        lineas = texto_completo.split('\n')
        datos = []
        en_seccion_comisiones = False
        inicio_encontrado = False
        
        for linea in lineas:
            # Verificar inicio de datos
            if "1. TOTAL OPERACIONES" in linea:
                inicio_encontrado = True
                continue
                
            if not inicio_encontrado:
                continue
                
            # Verificar sección de comisiones
            if "COMISIONES, IMPUESTOS Y ABONOS" in linea:
                en_seccion_comisiones = True
                continue
                
            # Ignorar líneas no deseadas
            if any(patron in linea for patron in PATRONES_IGNORAR):
                continue
                
            # Procesar la línea
            resultado = procesar_linea(linea, en_seccion_comisiones)
            if resultado:
                datos.append(resultado)
        
        if not datos:
            print("No se encontraron transacciones en el archivo")
            return None
            
        # Crear y procesar DataFrame
        df = pd.DataFrame(datos)
        df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce')
        
        print(f"\nSe procesaron {len(df)} transacciones")
        print("\nResumen por categoría:")
        print(df['Categoría'].value_counts())
        
        return df
        
    except Exception as e:
        print(f"Error procesando el PDF: {str(e)}")
        return None

def limpiar_y_ordenar_dataframe(df):
    """
    Elimina filas duplicadas y ordena un DataFrame por fecha.
    
    Args:
        df (pd.DataFrame): DataFrame a procesar. Debe contener las columnas 'Fecha', 'Descripción' y 'Monto'.
        
    Returns:
        pd.DataFrame: DataFrame limpio y ordenado, sin duplicados y ordenado por fecha.
    """

    df = pd.concat(df, ignore_index=True) 

    # Asegurarse de que la columna Fecha sea datetime
    df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d/%m/%Y', errors='coerce')
    
    # Eliminar filas duplicadas considerando todas las columnas
    df_limpio = df.drop_duplicates(subset=['Fecha', 'Descripción', 'Monto'], keep='first')
    
    # Ordenar por fecha de más antigua a más reciente
    df_ordenado = df_limpio.sort_values('Fecha')
    
    return df_ordenado

def exportar_archivos(df_final, df_abonos, directorio_salida="archivos_output"):
    """
    Exporta los DataFrames a archivos CSV en el directorio especificado.
    
    Args:
        df_final (pd.DataFrame): DataFrame con los gastos finales
        df_abonos (pd.DataFrame): DataFrame con los abonos
        directorio_salida (str): Directorio donde se guardarán los archivos (default: "archivos_output")
    """
    import os
    
    # Crear el directorio si no existe
    os.makedirs(directorio_salida, exist_ok=True)
    
    # Exportar gastos
    try:
        ruta_gastos = os.path.join(directorio_salida, "gastos hotboat.csv")
        df_final.to_csv(ruta_gastos, index=False)
    except PermissionError:
        print(f"Error: No se puede escribir el archivo '{ruta_gastos}'. Por favor, cierre cualquier programa que pueda tener el archivo abierto e intente nuevamente.")
    except Exception as e:
        print(f"Error inesperado al guardar gastos: {str(e)}")
    
    # Exportar abonos
    try:
        ruta_abonos = os.path.join(directorio_salida, "abonos hotboat.csv")
        df_abonos.to_csv(ruta_abonos, index=False)
    except PermissionError:
        print(f"Error: No se puede escribir el archivo '{ruta_abonos}'. Por favor, cierre cualquier programa que pueda tener el archivo abierto e intente nuevamente.")
    except Exception as e:
        print(f"Error inesperado al guardar abonos: {str(e)}")

def obtener_categoria(descripcion, diccionario_categorias):
    descripcion_normalizada = str(descripcion).strip().lower()
    for categoria, palabras_clave in diccionario_categorias.items():
        for palabra in palabras_clave:
            palabra_normalizada = str(palabra).strip().lower()
            if palabra_normalizada in descripcion_normalizada:
                return categoria
    return 'Sin categoría'

def categorizar_por_descripcion(df, diccionario_categorias):
    """
    Asigna una categoría a cada fila del DataFrame según la coincidencia de palabras clave en la columna 'Descripción'.
    diccionario_categorias debe ser un dict: {'Categoria1': [palabra1, palabra2, ...], ...}
    """
    df = df.copy()
    df['Categoría_2'] = df['Descripción'].apply(lambda desc: obtener_categoria(desc, diccionario_categorias))
    return df

def categorizar_por_diccionario(df, diccionario, nombre_columna):
    """
    Asigna una categoría a cada fila del DataFrame según la coincidencia de palabras clave en la columna 'Descripción'.
    El resultado se guarda en la columna nombre_columna. La comparación es insensible a mayúsculas/minúsculas y espacios.
    """
    df = df.copy()
    df[nombre_columna] = df['Descripción'].apply(obtener_categoria)
    return df

def reordenar_columna_categoria_extra(df):
    """
    Mueve la columna 'Categoría_2' a la cuarta posición y 'Categoría 1' a la quinta posición si existen.
    """
    cols = list(df.columns)
    # Mover 'Categoría_2' a la cuarta posición
    if 'Categoría_2' in cols:
        cols.insert(3, cols.pop(cols.index('Categoría_2')))
    # Mover 'Categoría 1' a la quinta posición (después de 'Categoría_2')
    if 'Categoría 1' in cols:
        idx_cat2 = cols.index('Categoría_2') if 'Categoría_2' in cols else 2
        cols.insert(idx_cat2 + 1, cols.pop(cols.index('Categoría 1')))
    df = df[cols]
    return df

def eliminar_filas_por_descripcion(df, lista_descripciones):
    """
    Elimina filas del DataFrame donde la columna 'Descripción' coincide (ignorando mayúsculas/minúsculas y espacios) con alguna de las descripciones en la lista.
    """
    if not lista_descripciones:
        return df
    descripciones_normalizadas = [d.strip().lower() for d in lista_descripciones]
    return df[~df['Descripción'].str.strip().str.lower().isin(descripciones_normalizadas)]


def procesar_df_final(df_banco_estado_cargos, df_banco_chile_facturado_internacional, df_banco_chile_facturado_nacional, diccionario_categorias, descripciones_a_eliminar=None, diccionario_categoria_1=None):

    df_final = pd.concat([
        df_banco_estado_cargos,
        df_banco_chile_facturado_internacional,
        df_banco_chile_facturado_nacional
    ], ignore_index=True, sort=False)
    df_final = eliminar_filas_por_descripcion(df_final, descripciones_a_eliminar)
    df_final['Fecha'] = pd.to_datetime(df_final['Fecha'], format='%d/%m/%Y', errors='coerce')
    df_final = df_final[df_final['Monto'] >= 0]
    df_final = df_final.drop_duplicates(subset=['Fecha', 'Descripción', 'Monto'], keep='first')
    
    # Primero categorizar por descripción para obtener Categoría_2
    df_final = categorizar_por_descripcion(df_final, diccionario_categorias)
    
    # Luego categorizar Categoría 1 basándose en Categoría_2
    if diccionario_categoria_1:
        df_final['Categoría 1'] = df_final['Categoría_2'].apply(lambda cat2: obtener_categoria(cat2, diccionario_categoria_1))
    
    df_final = reordenar_columna_categoria_extra(df_final)
    return df_final

# Función para crear la columna de fecha
def crear_columna_fecha(df):
    df['fecha'] = pd.to_datetime(df[['Año', 'mes', 'dia']].assign(
        Año=df['Año'].astype(str),
        mes=df['mes'].astype(str).str.zfill(2),
        dia=df['dia'].astype(str).str.zfill(2)
    ).agg('-'.join, axis=1))
    return df