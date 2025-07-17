import pandas as pd
import os

# Leer un archivo de cartola para ver su estructura
archivo_cartola = 'archivos_input/archivos_input_costos/cartola (4).xls'

try:
    # Leer todas las hojas del archivo
    excel_file = pd.ExcelFile(archivo_cartola)
    print(f"📄 Archivo: {archivo_cartola}")
    print(f"📋 Hojas disponibles: {excel_file.sheet_names}")
    
    # Revisar cada hoja
    for sheet_name in excel_file.sheet_names:
        print(f"\n{'='*50}")
        print(f"📋 HOJA: {sheet_name}")
        print(f"{'='*50}")
        
        df = pd.read_excel(archivo_cartola, sheet_name=sheet_name)
        print(f"📊 Estructura:")
        print(f"   Filas: {len(df)}")
        print(f"   Columnas: {len(df.columns)}")
        print(f"   Columnas: {list(df.columns)}")
        
        print(f"\n📋 Primeras 5 filas:")
        print(df.head(5))
        
        # Buscar filas con datos de transacciones
        print(f"\n🔍 Buscando filas con datos de transacciones...")
        for i, row in df.iterrows():
            if pd.notna(row.iloc[0]) and str(row.iloc[0]).strip():
                print(f"Fila {i}: {row.iloc[0]}")
                if i > 15:  # Solo mostrar las primeras 15 filas con datos
                    break
        
        print(f"\n📋 Últimas 3 filas:")
        print(df.tail(3))
    
except Exception as e:
    print(f"❌ Error leyendo archivo: {str(e)}") 