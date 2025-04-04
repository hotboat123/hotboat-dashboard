import pandas as pd


def ver_si_es_nacional_facturado(ruta_archivo):    
    # Leer el archivo de Excel y buscar la fila que contiene 'Categoría'
    df = pd.read_excel(ruta_archivo, sheet_name=0, header=None)  # Leemos sin encabezado
    # Encontrar la fila donde está la celda 'Categoría'
    categoria_fila = df[df.apply(lambda x: x.astype(str).str.contains('Descripción', case=False).any(), axis=1)].index[0]
    df_final = pd.read_excel(ruta_archivo, sheet_name=0, skiprows=categoria_fila, header=0)
    if "Monto Moneda Origen" in df_final.columns:
      return False
    return True

def ver_si_es_nacional_no_facturado(ruta_archivo):    
    # Leer el archivo de Excel y buscar la fila que contiene 'Categoría'
    df = pd.read_excel(ruta_archivo, sheet_name=0, header=None)  # Leemos sin encabezado
    # Encontrar la fila donde está la celda 'Categoría'
    categoria_fila = df[df.apply(lambda x: x.astype(str).str.contains('Descripción', case=False).any(), axis=1)].index[0]
    df_final = pd.read_excel(ruta_archivo, sheet_name=0, skiprows=categoria_fila, header=0)
    if "Monto (USD)" in df_final.columns:
      return False
    return True

# Función para leer el archivo Mov facturado
def leer_excel_mov_facturados_nacional(ruta_archivo):
    # Leer el archivo de Excel y buscar la fila que contiene 'Categoría'
    df = pd.read_excel(ruta_archivo, sheet_name=0, header=None)  # Leemos sin encabezado
    
    # Encontrar la fila donde está la celda 'Categoría'
    categoria_fila = df[df.apply(lambda x: x.astype(str).str.contains('Categoría', case=False).any(), axis=1)].index[0]

    # Leer el archivo nuevamente desde la fila que contiene 'Categoría', usando esa fila como header
    df_final = pd.read_excel(ruta_archivo, sheet_name=0, skiprows=categoria_fila, header=0)
    df_final=df_final[["Fecha","Descripción","Monto ($)","Cuotas","Categoría"]]
  
    return df_final

# Función para leer el archivo Mov No facturado
def leer_excel_mov_no_facturados_nacional(ruta_archivo):
    # Leer el archivo de Excel y buscar la fila que contiene 'Categoría'
    df = pd.read_excel(ruta_archivo, sheet_name=0, header=None)  # Leemos sin encabezado
    
    # Encontrar la fila donde está la celda 'Categoría'
    categoria_fila = df[df.apply(lambda x: x.astype(str).str.contains('Fecha', case=False).any(), axis=1)].index[0]

    # Leer el archivo nuevamente desde la fila que contiene 'Categoría', usando esa fila como header
    df_final = pd.read_excel(ruta_archivo, sheet_name=0, skiprows=categoria_fila, header=0)
    df_final["Monto ($)"] = df_final["Unnamed: 10"]
    df_final=df_final[["Fecha","Descripción","Cuotas","Monto ($)", "Ciudad"]]
  
    return df_final


# Función para leer el archivo Mov No facturado
def leer_excel_banco_estado(ruta_archivo, año_para_fecha_banco_estado):
    # Leer el archivo de Excel y buscar la fila que contiene 'Categoría'
    df = pd.read_excel(ruta_archivo, sheet_name="Movimientos", header=None)  # Leemos sin encabezado
    
    # Encontrar la fila donde está la celda 'Categoría'
    categoria_fila = df[df.apply(lambda x: x.astype(str).str.contains('Fecha', case=False).any(), axis=1)].index[0]

    # Leer el archivo nuevamente desde la fila que contiene 'Categoría', usando esa fila como header
    df_final = pd.read_excel(ruta_archivo, sheet_name="Movimientos", skiprows=categoria_fila, header=0)
    # Agregar el año "2025" a cada fecha
    df_final['Fecha'] = df_final['Fecha'] + '/' + año_para_fecha_banco_estado

    df_cargos = df_final[df_final['Cheques / Cargos'] > 0]
    df_abonos = df_final[df_final['Cheques / Cargos'] == 0]
    df_abonos["Monto ($)"] = df_abonos["Depósitos / Abonos"]
    df_abonos['Monto ($)'] = df_abonos['Monto ($)'].replace({'\$': '', '\.': ''}, regex=True).astype(int)
    df_abonos=df_abonos[["Fecha","Descripción","Monto ($)"]]
    df_cargos["Monto ($)"] = df_cargos["Cheques / Cargos"]
    df_cargos=df_cargos[["Fecha","Descripción","Monto ($)"]]
  
    return df_cargos, df_abonos
    

def leer_excel_mov_facturados_internacional(ruta_archivo, valor_aproximado_dolar):
    # Leer el archivo de Excel y buscar la fila que contiene 'Categoría'
    df = pd.read_excel(ruta_archivo, sheet_name=0, header=None)  # Leemos sin encabezado
    
    # Encontrar la fila donde está la celda 'Categoría'
    categoria_fila = df[df.apply(lambda x: x.astype(str).str.contains('Categoría', case=False).any(), axis=1)].index[0]

    # Leer el archivo nuevamente desde la fila que contiene 'Categoría', usando esa fila como header
    df_final = pd.read_excel(ruta_archivo, sheet_name=0, skiprows=categoria_fila, header=0)
    df_final['Monto ($)'] = df_final['Monto (USD)'] * valor_aproximado_dolar
    df_final=df_final[['Fecha', 'Descripción', 'Categoría', 'País', 'Monto ($)', 'Monto (USD)']]
    return df_final


def leer_excel_mov_no_facturados_internacional(ruta_archivo, valor_aproximado_dolar):
    # Leer el archivo de Excel y buscar la fila que contiene 'Categoría'
    df = pd.read_excel(ruta_archivo, sheet_name=0, header=None)  # Leemos sin encabezado
    
    # Encontrar la fila donde está la celda 'Categoría'
    categoria_fila = df[df.apply(lambda x: x.astype(str).str.contains('Fecha', case=False).any(), axis=1)].index[0]

    # Leer el archivo nuevamente desde la fila que contiene 'Categoría', usando esa fila como header
    df_final = pd.read_excel(ruta_archivo, sheet_name=0, skiprows=categoria_fila, header=0)
    df_final=df_final[['Fecha', 'Descripción', 'País', 'Monto (USD)']]
    df_final['Monto ($)'] = df_final['Monto (USD)'] * valor_aproximado_dolar
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