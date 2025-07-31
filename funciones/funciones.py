#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import os
import sys
from typing import Dict, List, Tuple, Optional
import re
from datetime import datetime, timedelta

# Configurar UTF-8 para que los emojis funcionen siempre
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    # Para versiones de Python < 3.7
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

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
    df_final=df_final[["Fecha","Descripción","Monto","Cuotas"]]  # Eliminada columna "Categoría"
  
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
    df_final['Monto'] = (df_final['Monto (USD)'].astype(float) * valor_aproximado_dolar).astype(int)
    df_final=df_final[['Fecha', 'Descripción', 'País', 'Monto', 'Monto (USD)']]  # Eliminada columna "Categoría"
    return df_final


def leer_excel_mov_no_facturados_internacional(ruta_archivo, valor_aproximado_dolar):
    # Leer el archivo de Excel y buscar la fila que contiene 'Categoría'
    df = pd.read_excel(ruta_archivo, sheet_name='Saldo y Mov No Facturado', header=None)  # Leemos sin encabezado
    
    # Encontrar la fila donde está la celda 'Categoría'
    descripcion_fila = df[df.apply(lambda x: x.astype(str).str.contains('Descripción', case=False).any(), axis=1)].index[0]

    # Leer el archivo nuevamente desde la fila que contiene 'Categoría', usando esa fila como header
    df_final = pd.read_excel(ruta_archivo, sheet_name='Saldo y Mov No Facturado', skiprows=descripcion_fila, header=0)
    df_final=df_final[['Fecha', 'Descripción', 'País', 'Monto (USD)']]
    df_final['Monto'] = (df_final['Monto (USD)'].astype(float) * valor_aproximado_dolar).astype(int)
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
    df[nombre_columna] = df['Descripción'].apply(lambda desc: obtener_categoria(desc, diccionario))
    return df

def reordenar_columna_categoria_extra(df):
    """
    Reordena las columnas en el orden deseado: Fecha, Monto, Categoría 1, Categoría_2, Observación, Descripción, resto de columnas.
    """
    cols = list(df.columns)
    
    # Definir el orden deseado para las columnas principales
    orden_principal = ['Fecha', 'Monto', 'Categoría 1', 'Categoría_2', 'Observación', 'Descripción']
    
    # Crear lista final de columnas
    cols_ordenadas = []
    
    # Agregar columnas principales en el orden deseado (solo si existen)
    for col in orden_principal:
        if col in cols:
            cols_ordenadas.append(col)
            cols.remove(col)  # Remover de la lista original
    
    # Agregar las columnas restantes al final
    cols_ordenadas.extend(cols)
    
    # Reordenar el DataFrame
    df = df[cols_ordenadas]
    return df

def eliminar_filas_por_descripcion(df, lista_descripciones):
    """
    Elimina filas del DataFrame donde la columna 'Descripción' coincide (ignorando mayúsculas/minúsculas y espacios) con alguna de las descripciones en la lista.
    """
    if not lista_descripciones:
        return df
    descripciones_normalizadas = [d.strip().lower() for d in lista_descripciones]
    return df[~df['Descripción'].str.strip().str.lower().isin(descripciones_normalizadas)]


def eliminar_filas_por_fecha_monto(df, lista_fecha_monto):
    """
    Elimina filas específicas del DataFrame basándose en combinaciones de fecha y monto.
    
    Args:
        df (pd.DataFrame): DataFrame a procesar. Debe contener las columnas 'Fecha' y 'Monto'.
        lista_fecha_monto (List[List]): Lista de listas con formato [fecha, monto] a eliminar.
                                       Fecha puede ser string 'YYYY-MM-DD' o 'DD/MM/YYYY'
                                       Monto debe ser numérico
    
    Returns:
        pd.DataFrame: DataFrame sin las filas especificadas
        
    Ejemplo:
        lista_eliminaciones = [
            ['2025-07-15', 50000],
            ['15/07/2025', 25000],
            ['2025-06-01', 100000]
        ]
    """
    if not lista_fecha_monto or df.empty:
        return df
    
    print(f"🗑️ Eliminando {len(lista_fecha_monto)} registros específicos por fecha y monto...")
    
    # Asegurar que la columna Fecha sea datetime
    df_copia = df.copy()
    if 'Fecha' in df_copia.columns:
        df_copia = convertir_fechas_a_datetime(df_copia, 'Fecha')
    
    filas_iniciales = len(df_copia)
    
    # Crear máscara para identificar filas a eliminar
    mask_eliminar = pd.Series([False] * len(df_copia), index=df_copia.index)
    
    for fecha_str, monto in lista_fecha_monto:
        try:
            # Convertir fecha string a datetime
            if isinstance(fecha_str, str):
                # Intentar diferentes formatos
                fecha_dt = None
                formatos = ['%Y-%m-%d', '%d/%m/%Y', '%d/%m/%y']
                for formato in formatos:
                    try:
                        fecha_dt = pd.to_datetime(fecha_str, format=formato)
                        break
                    except:
                        continue
                
                if fecha_dt is None:
                    # Último intento con parse automático
                    try:
                        fecha_dt = pd.to_datetime(fecha_str)
                    except:
                        print(f"   ⚠️  No se pudo convertir fecha: {fecha_str}")
                        continue
            else:
                fecha_dt = pd.to_datetime(fecha_str)
            
            # Buscar filas que coincidan en fecha y monto
            mask_fecha = df_copia['Fecha'].dt.date == fecha_dt.date()
            mask_monto = df_copia['Monto'] == monto
            mask_coincidencia = mask_fecha & mask_monto
            
            if mask_coincidencia.any():
                mask_eliminar = mask_eliminar | mask_coincidencia
                print(f"   ✅ Marcados para eliminar: {mask_coincidencia.sum()} registros con fecha {fecha_dt.date()} y monto ${monto:,.0f}")
            else:
                print(f"   ⚠️  No se encontraron registros con fecha {fecha_dt.date()} y monto ${monto:,.0f}")
                
        except Exception as e:
            print(f"   ❌ Error procesando eliminación {fecha_str}, {monto}: {str(e)}")
    
    # Eliminar las filas marcadas
    df_resultado = df_copia[~mask_eliminar]
    filas_eliminadas = filas_iniciales - len(df_resultado)
    
    if filas_eliminadas > 0:
        print(f"✅ Se eliminaron {filas_eliminadas} filas específicas")
    else:
        print("ℹ️  No se eliminaron filas")
    
    return df_resultado


def limpiar_cuotas_01_01(df):
    """
    Limpia la columna 'Cuotas' convirtiendo valores "01/01" en campos vacíos.
    
    Args:
        df (pd.DataFrame): DataFrame a procesar
        
    Returns:
        pd.DataFrame: DataFrame con columna 'Cuotas' limpia
    """
    if df.empty or 'Cuotas' not in df.columns:
        return df
    
    df_copia = df.copy()
    
    # Contar cuántos valores "01/01" hay antes de la limpieza
    valores_01_01 = df_copia['Cuotas'].astype(str).str.strip().str.lower() == '01/01'
    count_01_01 = valores_01_01.sum()
    
    if count_01_01 > 0:
        print(f"🧹 Limpiando {count_01_01} valores '01/01' de la columna Cuotas...")
        
        # Reemplazar valores "01/01" con cadena vacía
        # Manejar diferentes variaciones: "01/01", " 01/01 ", "01/01", etc.
        df_copia.loc[valores_01_01, 'Cuotas'] = ''
        
        print(f"✅ Se limpiaron {count_01_01} valores '01/01' en la columna Cuotas")
    else:
        print("ℹ️  No se encontraron valores '01/01' en la columna Cuotas")
    
    return df_copia


def agregar_columnas_origen(df_banco_estado_cargos, df_banco_chile_facturado_internacional, df_banco_chile_facturado_nacional, df_banco_chile_no_facturado_internacional, df_banco_chile_no_facturado_nacional, df_cuenta_corriente_cargos):
    """
    Agrega la columna 'Origen' a cada DataFrame y los recopila en una lista.
    
    Args:
        df_banco_estado_cargos: DataFrame de cargos del Banco Estado
        df_banco_chile_facturado_internacional: DataFrame de movimientos facturados internacionales
        df_banco_chile_facturado_nacional: DataFrame de movimientos facturados nacionales
        df_banco_chile_no_facturado_internacional: DataFrame de movimientos no facturados internacionales
        df_banco_chile_no_facturado_nacional: DataFrame de movimientos no facturados nacionales
        df_cuenta_corriente_cargos: DataFrame de cargos de cuenta corriente
        
    Returns:
        List[pd.DataFrame]: Lista de DataFrames con columna 'Origen' agregada
    """
    dataframes_con_origen = []
    
    if not df_banco_estado_cargos.empty:
        df_banco_estado_cargos = df_banco_estado_cargos.copy()
        df_banco_estado_cargos['Origen'] = 'Banco Estado'
        dataframes_con_origen.append(df_banco_estado_cargos)
    
    if not df_banco_chile_facturado_internacional.empty:
        df_banco_chile_facturado_internacional = df_banco_chile_facturado_internacional.copy()
        df_banco_chile_facturado_internacional['Origen'] = 'Mov. Facturado Internacional'
        dataframes_con_origen.append(df_banco_chile_facturado_internacional)
    
    if not df_banco_chile_facturado_nacional.empty:
        df_banco_chile_facturado_nacional = df_banco_chile_facturado_nacional.copy()
        df_banco_chile_facturado_nacional['Origen'] = 'Mov. Facturado Nacional'
        dataframes_con_origen.append(df_banco_chile_facturado_nacional)
    
    if not df_banco_chile_no_facturado_internacional.empty:
        df_banco_chile_no_facturado_internacional = df_banco_chile_no_facturado_internacional.copy()
        df_banco_chile_no_facturado_internacional['Origen'] = 'Mov. No Facturado Internacional'
        dataframes_con_origen.append(df_banco_chile_no_facturado_internacional)
    
    if not df_banco_chile_no_facturado_nacional.empty:
        df_banco_chile_no_facturado_nacional = df_banco_chile_no_facturado_nacional.copy()
        df_banco_chile_no_facturado_nacional['Origen'] = 'Mov. No Facturado Nacional'
        dataframes_con_origen.append(df_banco_chile_no_facturado_nacional)
    
    if not df_cuenta_corriente_cargos.empty:
        df_cuenta_corriente_cargos = df_cuenta_corriente_cargos.copy()
        df_cuenta_corriente_cargos['Origen'] = 'Cuenta Corriente'
        dataframes_con_origen.append(df_cuenta_corriente_cargos)
    
    return dataframes_con_origen

def crear_tabla_correcciones(lista_correcciones):
    """
    Convierte una lista de listas en un DataFrame para correcciones de categorías.
    
    Args:
        lista_correcciones (List[List]): Lista de listas con formato:
            [fecha, descripcion, monto, categoria_1, categoria_2, observacion]
            
    Returns:
        pd.DataFrame: DataFrame con las correcciones a aplicar
    """
    if not lista_correcciones:
        return pd.DataFrame()
    
    columnas = ['Fecha', 'Descripción', 'Monto', 'Categoría 1', 'Categoría_2', 'Observación']
    df_correcciones = pd.DataFrame(lista_correcciones, columns=columnas)
    
    # Convertir fechas a datetime
    df_correcciones = convertir_fechas_a_datetime(df_correcciones, 'Fecha')
    
    # Asegurar que el monto sea numérico
    df_correcciones['Monto'] = pd.to_numeric(df_correcciones['Monto'], errors='coerce')
    
    return df_correcciones

def aplicar_correcciones_categorias(df_final, tabla_correcciones_lista):
    """
    Aplica correcciones de categorías desde una tabla externa al DataFrame final.
    
    Args:
        df_final (pd.DataFrame): DataFrame con los datos procesados
        tabla_correcciones_lista (List[List]): Lista de listas con correcciones
        
    Returns:
        pd.DataFrame: DataFrame con correcciones aplicadas
    """
    if not tabla_correcciones_lista:
        return df_final
    
    # Crear DataFrame de correcciones
    df_correcciones = crear_tabla_correcciones(tabla_correcciones_lista)
    
    if df_correcciones.empty:
        return df_final
    
    print(f"📝 Aplicando {len(df_correcciones)} correcciones de categorías...")
    
    # Crear columna Observación si no existe
    if 'Observación' not in df_final.columns:
        df_final['Observación'] = ''
    
    # Hacer merge para identificar las filas a corregir (solo por fecha y monto)
    df_merged = df_final.merge(
        df_correcciones[['Fecha', 'Monto', 'Categoría 1', 'Categoría_2', 'Observación']], 
        on=['Fecha', 'Monto'], 
        how='left', 
        suffixes=('', '_corr')
    )
    
    # Aplicar correcciones donde existan
    correcciones_aplicadas = 0
    for col in ['Categoría_2', 'Categoría 1', 'Observación']:
        col_corr = f"{col}_corr"
        if col_corr in df_merged.columns:
            mask = df_merged[col_corr].notna()
            df_merged.loc[mask, col] = df_merged.loc[mask, col_corr]
            correcciones_aplicadas += mask.sum()
    
    # Eliminar columnas temporales
    cols_to_drop = [col for col in df_merged.columns if col.endswith('_corr')]
    df_merged = df_merged.drop(columns=cols_to_drop)
    
    print(f"✅ Se aplicaron correcciones a {correcciones_aplicadas} registros")
    
    return df_merged

def procesar_df_final(df_banco_estado_cargos, df_banco_chile_facturado_internacional, df_banco_chile_facturado_nacional, df_banco_chile_no_facturado_internacional, df_banco_chile_no_facturado_nacional, df_cuenta_corriente_cargos, diccionario_categorias, descripciones_a_eliminar=None, diccionario_categoria_1=None, tabla_correcciones=None, eliminaciones_fecha_monto=None):

    # Agregar columna "Origen" a cada DataFrame antes de concatenar
    dataframes_con_origen = agregar_columnas_origen(
        df_banco_estado_cargos, 
        df_banco_chile_facturado_internacional, 
        df_banco_chile_facturado_nacional, 
        df_banco_chile_no_facturado_internacional, 
        df_banco_chile_no_facturado_nacional, 
        df_cuenta_corriente_cargos
    )
    
    # Concatenar todos los DataFrames con la columna "Origen"
    df_final = pd.concat(dataframes_con_origen, ignore_index=True, sort=False) if dataframes_con_origen else pd.DataFrame()
    df_final = eliminar_filas_por_descripcion(df_final, descripciones_a_eliminar)
    df_final = eliminar_filas_por_fecha_monto(df_final, eliminaciones_fecha_monto)
    
    # Convertir fechas a datetime usando la nueva función
    df_final = convertir_fechas_a_datetime(df_final, 'Fecha')
    
    # Limpiar valores "01/01" en columna Cuotas antes de eliminar duplicados
    df_final = limpiar_cuotas_01_01(df_final)
    
    #Eliminar duplicados y negativos
    df_final = df_final[df_final['Monto'] >= 0]
    df_final = df_final.drop_duplicates(subset=['Fecha', 'Descripción', 'Monto', 'Cuotas'], keep='first')
    
    # Categorizar todos los datos usando el diccionario (incluyendo cuenta corriente)
    df_final = categorizar_por_descripcion(df_final, diccionario_categorias)
    
    # Luego categorizar Categoría 1 basándose en Categoría_2
    if diccionario_categoria_1:
        df_final['Categoría 1'] = df_final['Categoría_2'].apply(lambda cat2: obtener_categoria(cat2, diccionario_categoria_1))
    
    df_final = reordenar_columna_categoria_extra(df_final)
    
    # Aplicar correcciones de categorías si se proporcionaron
    if tabla_correcciones:
        df_final = aplicar_correcciones_categorias(df_final, tabla_correcciones)
    
    return df_final

# Función para crear la columna de fecha
def crear_columna_fecha(df):
    df['fecha'] = pd.to_datetime(df[['Año', 'mes', 'dia']].assign(
        Año=df['Año'].astype(str),
        mes=df['mes'].astype(str).str.zfill(2),
        dia=df['dia'].astype(str).str.zfill(2)
    ).agg('-'.join, axis=1))
    return df

# ======== FUNCIONES PARA PROCESAMIENTO DE ARCHIVOS ========

class ProcesadorArchivos:
    """Clase para procesar archivos financieros de HotBoat"""
    
    def __init__(self):
        self.df_banco_estado_abonos = []
        self.df_banco_estado_cargos = []
        self.df_banco_chile_facturado_nacional = []
        self.df_banco_chile_facturado_internacional = []
        self.df_banco_chile_no_facturado_nacional = []
        self.df_banco_chile_no_facturado_internacional = []
        self.df_cuenta_corriente_cargos = []
        self.df_cuenta_corriente_abonos = []
        
    def procesar_archivo(self, ruta_archivo: str, nombre_archivo: str, valor_aproximado_dolar: float, año_para_fecha_banco_estado: str) -> bool:
        """
        Procesa un archivo Excel según su tipo
        
        Args:
            ruta_archivo: Ruta completa del archivo
            nombre_archivo: Nombre del archivo
            valor_aproximado_dolar: Valor del dólar para conversiones
            año_para_fecha_banco_estado: Año para fechas del banco estado
            
        Returns:
            bool: True si se procesó correctamente, False en caso contrario
        """
        try:
            print(f"📄 Procesando: {nombre_archivo}")
            
            # Procesar archivos de Chequera (Banco Estado)
            if "Chequera" in nombre_archivo:
                print(f"   ✅ Archivo de Chequera detectado")
                df_cargos, df_abonos = leer_excel_banco_estado(ruta_archivo, año_para_fecha_banco_estado)
                self.df_banco_estado_abonos.append(df_abonos)
                self.df_banco_estado_cargos.append(df_cargos)
                return True
                
            # Procesar archivos de Cartola (Cuenta Corriente)
            elif "cartola" in nombre_archivo.lower():
                print(f"   ✅ Archivo Cartola (Cuenta Corriente) detectado")
                try:
                    cargos, abonos = leer_cartola_cuenta_corriente(ruta_archivo)
                    if not cargos.empty:
                        self.df_cuenta_corriente_cargos.append(cargos)
                        print(f"      💳 Cargos cuenta corriente: {len(cargos)} filas")
                    if not abonos.empty:
                        self.df_cuenta_corriente_abonos.append(abonos)
                        print(f"      💳 Abonos cuenta corriente: {len(abonos)} filas")
                    return True
                except Exception as e:
                    print(f"   ❌ Error procesando cartola: {str(e)}")
                    return False
                
            # Procesar archivos de Movimientos Facturados (Banco Chile)
            elif "Mov_Facturado" in nombre_archivo:
                print(f"   ✅ Archivo Mov_Facturado detectado")
                if ver_si_es_nacional_facturado(ruta_archivo):
                    print(f"      📍 Tipo: Nacional")
                    df = leer_excel_mov_facturados_nacional(ruta_archivo)
                    self.df_banco_chile_facturado_nacional.append(df)
                else:
                    print(f"      🌍 Tipo: Internacional")
                    df = leer_excel_mov_facturados_internacional(ruta_archivo, valor_aproximado_dolar)
                    self.df_banco_chile_facturado_internacional.append(df)
                return True
                
            # Procesar archivos de Movimientos No Facturados (Banco Chile)
            elif "Saldo_y_Mov_No_Facturado" in nombre_archivo:
                print(f"   ✅ Archivo Saldo_y_Mov_No_Facturado detectado")
                if ver_si_es_nacional_no_facturado(ruta_archivo):
                    print(f"      📍 Tipo: Nacional")
                    df = leer_excel_mov_no_facturados_nacional(ruta_archivo)
                    self.df_banco_chile_no_facturado_nacional.append(df)
                else:
                    print(f"      🌍 Tipo: Internacional")
                    df = leer_excel_mov_no_facturados_internacional(ruta_archivo, valor_aproximado_dolar)
                    self.df_banco_chile_no_facturado_internacional.append(df)
                return True
                
            else:
                print(f"   ⚠️  Archivo no reconocido: {nombre_archivo}")
                print(f"      💡 Tipos soportados: Chequera, Mov_Facturado, Saldo_y_Mov_No_Facturado, cartola")
                return False
                
        except Exception as e:
            print(f"   ❌ Error procesando {nombre_archivo}: {str(e)}")
            return False
    
    def consolidar_datos(self) -> dict:
        """
        Consolida todos los datos procesados
        
        Returns:
            Dict con DataFrames consolidados
        """
        print("=" * 60)
        print("🔄 CONSOLIDANDO DATOS...")
        
        datos_consolidados = {}
        
        # Consolidar Banco Estado
        if self.df_banco_estado_abonos:
            datos_consolidados['banco_estado_abonos'] = limpiar_y_ordenar_dataframe(self.df_banco_estado_abonos)
            print(f"✅ Abonos Banco Estado: {len(datos_consolidados['banco_estado_abonos'])} registros")
        else:
            datos_consolidados['banco_estado_abonos'] = pd.DataFrame()
            print("⚠️  No se encontraron archivos de abonos Banco Estado")
            
        if self.df_banco_estado_cargos:
            datos_consolidados['banco_estado_cargos'] = limpiar_y_ordenar_dataframe(self.df_banco_estado_cargos)
            print(f"✅ Cargos Banco Estado: {len(datos_consolidados['banco_estado_cargos'])} registros")
        else:
            datos_consolidados['banco_estado_cargos'] = pd.DataFrame()
            print("⚠️  No se encontraron archivos de cargos Banco Estado")
        
        # Consolidar Banco Chile Facturado
        if self.df_banco_chile_facturado_internacional:
            datos_consolidados['banco_chile_facturado_internacional'] = pd.concat(
                self.df_banco_chile_facturado_internacional, ignore_index=True
            )
            print(f"✅ Movimientos Facturados Internacional: {len(datos_consolidados['banco_chile_facturado_internacional'])} registros")
        else:
            datos_consolidados['banco_chile_facturado_internacional'] = pd.DataFrame()
            print("⚠️  No se encontraron archivos de movimientos facturados internacionales")
            
        if self.df_banco_chile_facturado_nacional:
            datos_consolidados['banco_chile_facturado_nacional'] = pd.concat(
                self.df_banco_chile_facturado_nacional, ignore_index=True
            )
            print(f"✅ Movimientos Facturados Nacional: {len(datos_consolidados['banco_chile_facturado_nacional'])} registros")
        else:
            datos_consolidados['banco_chile_facturado_nacional'] = pd.DataFrame()
            print("⚠️  No se encontraron archivos de movimientos facturados nacionales")
        
        # Consolidar Banco Chile No Facturado
        if self.df_banco_chile_no_facturado_internacional:
            datos_consolidados['banco_chile_no_facturado_internacional'] = pd.concat(
                self.df_banco_chile_no_facturado_internacional, ignore_index=True
            )
            print(f"✅ Movimientos No Facturados Internacional: {len(datos_consolidados['banco_chile_no_facturado_internacional'])} registros")
        else:
            datos_consolidados['banco_chile_no_facturado_internacional'] = pd.DataFrame()
            print("⚠️  No se encontraron archivos de movimientos no facturados internacionales")
            
        if self.df_banco_chile_no_facturado_nacional:
            datos_consolidados['banco_chile_no_facturado_nacional'] = pd.concat(
                self.df_banco_chile_no_facturado_nacional, ignore_index=True
            )
            print(f"✅ Movimientos No Facturados Nacional: {len(datos_consolidados['banco_chile_no_facturado_nacional'])} registros")
        else:
            datos_consolidados['banco_chile_no_facturado_nacional'] = pd.DataFrame()
            print("⚠️  No se encontraron archivos de movimientos no facturados nacionales")
        
        # Consolidar Cuenta Corriente
        if self.df_cuenta_corriente_cargos:
            # Asegurar que la columna se llame 'Fecha'
            for i, df in enumerate(self.df_cuenta_corriente_cargos):
                if 'fecha' in df.columns and 'Fecha' not in df.columns:
                    self.df_cuenta_corriente_cargos[i] = df.rename(columns={'fecha': 'Fecha'})
            
            datos_consolidados['cuenta_corriente_cargos'] = pd.concat(
                self.df_cuenta_corriente_cargos, ignore_index=True
            )
            datos_consolidados['cuenta_corriente_cargos'] = datos_consolidados['cuenta_corriente_cargos'].drop_duplicates(subset=['Fecha', 'Descripción', 'Monto'], keep='first')
            print(f"✅ Cargos Cuenta Corriente: {len(datos_consolidados['cuenta_corriente_cargos'])} registros")
        else:
            datos_consolidados['cuenta_corriente_cargos'] = pd.DataFrame()
            print("⚠️  No se encontraron archivos de cargos cuenta corriente")
            
        if self.df_cuenta_corriente_abonos:
            # Asegurar que la columna se llame 'Fecha'
            for i, df in enumerate(self.df_cuenta_corriente_abonos):
                if 'fecha' in df.columns and 'Fecha' not in df.columns:
                    self.df_cuenta_corriente_abonos[i] = df.rename(columns={'fecha': 'Fecha'})
            
            datos_consolidados['cuenta_corriente_abonos'] = pd.concat(
                self.df_cuenta_corriente_abonos, ignore_index=True
            )
            datos_consolidados['cuenta_corriente_abonos'] = datos_consolidados['cuenta_corriente_abonos'].drop_duplicates(subset=['Fecha', 'Descripción', 'Monto'], keep='first')
            print(f"✅ Abonos Cuenta Corriente: {len(datos_consolidados['cuenta_corriente_abonos'])} registros")
        else:
            datos_consolidados['cuenta_corriente_abonos'] = pd.DataFrame()
            print("⚠️  No se encontraron archivos de abonos cuenta corriente")
        
        return datos_consolidados

def procesar_archivos_financieros(valor_aproximado_dolar: float,
                                 directorio_input: str = 'archivos_input/archivos_input_costos', 
                                 directorio_output: str = 'archivos_output',
                                 año_para_fecha_banco_estado: str = '2025',
                                 diccionario_categorias: dict = None,
                                 descripciones_a_eliminar: list = None,
                                 diccionario_categoria_1: dict = None,
                                 tabla_correcciones: list = None,
                                 eliminaciones_fecha_monto: list = None) -> bool:
    """
    Función principal que procesa todos los archivos financieros
    
    Args:
        directorio_input: Directorio con archivos de entrada
        directorio_output: Directorio para archivos de salida
        valor_aproximado_dolar: Valor del dólar para conversiones
        año_para_fecha_banco_estado: Año para fechas del banco estado
        diccionario_categorias: Diccionario de categorías
        descripciones_a_eliminar: Lista de descripciones a eliminar
        diccionario_categoria_1: Diccionario de categorías principales
        tabla_correcciones: Lista de listas con correcciones de categorías
        eliminaciones_fecha_monto: Lista de listas con [fecha, monto] a eliminar
        
    Returns:
        bool: True si el procesamiento fue exitoso
    """
    print("🚤" * 20)
    print("🚤 PROCESADOR DE GASTOS Y COSTOS HOTBOAT")
    print("🚤" * 20)
    print()
    print("🔄 PROCESANDO ARCHIVOS DE COSTOS Y GASTOS...")
    print("=" * 60)
    
    # Verificar que existe el directorio de entrada
    if not os.path.exists(directorio_input):
        print(f"❌ ERROR: No existe el directorio {directorio_input}")
        print("💡 Asegúrate de tener los archivos en la carpeta correcta")
        return False
    
    # Inicializar procesador
    procesador = ProcesadorArchivos()
    archivos_procesados = 0
    archivos_con_error = 0
    
    # Procesar cada archivo en el directorio
    for archivo in os.listdir(directorio_input):
        ruta_archivo = os.path.join(directorio_input, archivo)
        
        # Procesar solo archivos Excel
        if archivo.endswith((".xlsx", ".xls")):
            if procesador.procesar_archivo(ruta_archivo, archivo, valor_aproximado_dolar, año_para_fecha_banco_estado):
                archivos_procesados += 1
            else:
                archivos_con_error += 1
        else:
            print(f"⚠️  Archivo no soportado: {archivo}")
    
    # Consolidar datos
    datos_consolidados = procesador.consolidar_datos()
    
    print("=" * 60)
    print("🔄 PROCESANDO DATOS FINALES...")
    
    # Procesar DataFrame final con gastos
    df_final = procesar_df_final(
        datos_consolidados['banco_estado_cargos'],
        datos_consolidados['banco_chile_facturado_internacional'],
        datos_consolidados['banco_chile_facturado_nacional'],
        datos_consolidados['banco_chile_no_facturado_internacional'],
        datos_consolidados['banco_chile_no_facturado_nacional'],
        datos_consolidados['cuenta_corriente_cargos'],
        diccionario_categorias,
        descripciones_a_eliminar,
        diccionario_categoria_1,
        tabla_correcciones,
        eliminaciones_fecha_monto
    )
    
    # Procesar abonos
    df_abonos = pd.DataFrame()
    if not datos_consolidados['banco_estado_abonos'].empty:
        df_banco_estado_abonos = datos_consolidados['banco_estado_abonos'].copy()
        df_banco_estado_abonos['Fecha'] = pd.to_datetime(df_banco_estado_abonos['Fecha'], format='%d/%m/%Y', errors='coerce')
        df_abonos = pd.concat([df_banco_estado_abonos], axis=0)
    
    # Agregar abonos de cuenta corriente
    if not datos_consolidados['cuenta_corriente_abonos'].empty:
        df_abonos_cc = datos_consolidados['cuenta_corriente_abonos'].copy()
        df_abonos_cc['Fecha'] = pd.to_datetime(df_abonos_cc['Fecha'], format='%d/%m/%Y', errors='coerce')
        df_abonos = pd.concat([df_abonos, df_abonos_cc], axis=0)
    
    print("=" * 60)
    print("💾 EXPORTANDO ARCHIVOS...")
    
    # Exportar archivos
    try:
        exportar_archivos(df_final, df_abonos, directorio_output)
        

        print("✅ PROCESAMIENTO COMPLETADO EXITOSAMENTE")
        print("=" * 60)
        print(f"📊 RESUMEN:")
        print(f"   ✅ Archivos procesados: {archivos_procesados}")
        print(f"   ❌ Archivos con error: {archivos_con_error}")
        print(f"   📈 Gastos totales: {len(df_final)} registros")
        print(f"   💰 Abonos totales: {len(df_abonos)} registros")

        return True
        
    except Exception as e:
        print(f"❌ Error exportando archivos: {str(e)}")
        return False

def leer_cartola_cuenta_corriente(ruta_archivo):
    """
    Lee una cartola de cuenta corriente buscando dinámicamente donde empieza la tabla
    (donde aparecen "fecha" y "descripción"), y separa en cargos y abonos con columna 'Monto'.
    Devuelve dos DataFrames: cargos y abonos.
    """
    # Leer la hoja principal sin encabezado
    df = pd.read_excel(ruta_archivo, sheet_name='Hoja1', header=None)
    
    # Buscar la fila donde aparecen "fecha" y "descripción"
    fila_encabezados = None
    for i, row in df.iterrows():
        row_str = ' '.join(str(cell).lower() for cell in row if pd.notna(cell))
        if 'fecha' in row_str and 'descrip' in row_str:
            fila_encabezados = i
            break
    
    if fila_encabezados is None:
        print(f"⚠️ No se encontró la tabla con 'fecha' y 'descripción' en {ruta_archivo}")
        return pd.DataFrame(), pd.DataFrame()
    
    # Tomar encabezados desde la fila encontrada
    headers = df.iloc[fila_encabezados].tolist()
    
    # Leer la tabla de transacciones desde la siguiente fila
    df_transacciones = pd.read_excel(ruta_archivo, sheet_name='Hoja1', skiprows=fila_encabezados + 1, header=None)
    df_transacciones.columns = headers
    
    # Limpiar filas vacías
    df_transacciones = df_transacciones.dropna(how='all')
    
    # Estandarizar nombres de columnas
    columnas_map = {}
    for col in df_transacciones.columns:
        col_str = str(col).strip().lower()
        if 'fecha' in col_str:
            columnas_map[col] = 'Fecha'
        elif 'descrip' in col_str:
            columnas_map[col] = 'Descripción'
        elif 'cargo' in col_str and 'clp' in col_str:
            columnas_map[col] = 'Cargos (CLP)'
        elif 'abono' in col_str and 'clp' in col_str:
            columnas_map[col] = 'Abonos (CLP)'
        else:
            columnas_map[col] = col
    
    df_transacciones = df_transacciones.rename(columns=columnas_map)
    
    # Verificar que tenemos las columnas necesarias
    if 'Fecha' not in df_transacciones.columns or 'Descripción' not in df_transacciones.columns:
        print(f"⚠️ Faltan columnas 'Fecha' o 'Descripción' en {ruta_archivo}")
        print(f"   Columnas disponibles: {list(df_transacciones.columns)}")
        return pd.DataFrame(), pd.DataFrame()
    if 'Cargos (CLP)' not in df_transacciones.columns and 'Abonos (CLP)' not in df_transacciones.columns:
        print(f"⚠️ No se encontraron columnas 'Cargos (CLP)' ni 'Abonos (CLP)' en {ruta_archivo}")
        print(f"   Columnas disponibles: {list(df_transacciones.columns)}")
        return pd.DataFrame(), pd.DataFrame()
    
    # Procesar cargos
    cargos = pd.DataFrame()
    if 'Cargos (CLP)' in df_transacciones.columns:
        cargos = df_transacciones[['Fecha', 'Descripción', 'Cargos (CLP)']].copy()
        cargos = cargos[pd.to_numeric(cargos['Cargos (CLP)'], errors='coerce').notna()]
        cargos['Monto'] = abs(pd.to_numeric(cargos['Cargos (CLP)'], errors='coerce'))
        cargos = cargos.drop(columns=['Cargos (CLP)'])
        cargos = cargos[pd.to_datetime(cargos['Fecha'], errors='coerce', dayfirst=True).notna()]
        cargos = cargos.drop_duplicates(subset=['Fecha', 'Descripción', 'Monto'], keep='first')
        
        # Estandarizar formato de fecha a dd/mm/YYYY (consistente con otros datos)
        if not cargos.empty:
            # Mantener como datetime en lugar de convertir a string
            cargos['Fecha'] = pd.to_datetime(cargos['Fecha'], errors='coerce', dayfirst=True)
    
    # Procesar abonos
    abonos = pd.DataFrame()
    if 'Abonos (CLP)' in df_transacciones.columns:
        abonos = df_transacciones[['Fecha', 'Descripción', 'Abonos (CLP)']].copy()
        abonos = abonos[pd.to_numeric(abonos['Abonos (CLP)'], errors='coerce').notna()]
        abonos['Monto'] = abs(pd.to_numeric(abonos['Abonos (CLP)'], errors='coerce'))
        abonos = abonos.drop(columns=['Abonos (CLP)'])
        abonos = abonos[pd.to_datetime(abonos['Fecha'], errors='coerce', dayfirst=True).notna()]
        abonos = abonos.drop_duplicates(subset=['Fecha', 'Descripción', 'Monto'], keep='first')
        
        # Estandarizar formato de fecha a dd/mm/YYYY (consistente con otros datos)
        if not abonos.empty:
            abonos['Fecha'] = pd.to_datetime(abonos['Fecha'], errors='coerce', dayfirst=True)
    
    return cargos, abonos

def convertir_fechas_a_datetime(df, columna_fecha='Fecha'):
    """
    Convierte fechas en formato string a datetime, manejando múltiples formatos.
    
    Args:
        df: DataFrame con la columna de fechas
        columna_fecha: Nombre de la columna de fechas (default: 'Fecha')
    
    Returns:
        DataFrame con fechas convertidas a datetime
    """
    df = df.copy()
    
    # Solo procesar si la columna existe y no está vacía
    if columna_fecha not in df.columns or df.empty:
        return df
    
    # Si ya es datetime, no hacer nada
    if pd.api.types.is_datetime64_any_dtype(df[columna_fecha]):
        return df
    
    # Convertir a string si no lo es
    if not pd.api.types.is_string_dtype(df[columna_fecha]):
        df[columna_fecha] = df[columna_fecha].astype(str)
    
    # Función para convertir una fecha individual
    def convertir_fecha(fecha_str):
        if pd.isna(fecha_str) or fecha_str == '' or fecha_str == 'nan':
            return pd.NaT
        
        fecha_str = str(fecha_str).strip()
        
        # Intentar formato ISO (2025-04-30 00:00:00)
        try:
            return pd.to_datetime(fecha_str, format='%Y-%m-%d %H:%M:%S')
        except:
            pass
        
        # Intentar formato ISO sin hora (2025-04-30)
        try:
            return pd.to_datetime(fecha_str, format='%Y-%m-%d')
        except:
            pass
        
        # Intentar formato dd/mm/yyyy (12/02/2025)
        try:
            return pd.to_datetime(fecha_str, format='%d/%m/%Y')
        except:
            pass
        
        # Intentar formato dd/mm/yy (12/02/25)
        try:
            return pd.to_datetime(fecha_str, format='%d/%m/%y')
        except:
            pass
        
        # Si nada funciona, intentar parse automático
        try:
            return pd.to_datetime(fecha_str)
        except:
            return pd.NaT
    
    # Aplicar la conversión
    df[columna_fecha] = df[columna_fecha].apply(convertir_fecha)
    
    return df