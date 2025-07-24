#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 BÚSQUEDA DE TRASPASO A HECTOR LLANCAO
=======================================
Script para encontrar de qué origen proviene el traspaso a Hector Llancao.
"""

import pandas as pd
import os

def buscar_llancao():
    print('🔍 BUSCANDO TRASPASO A HECTOR LLANCAO')
    print('='*50)
    
    archivo_gastos = 'archivos_output/gastos hotboat.csv'
    
    if not os.path.exists(archivo_gastos):
        print(f'❌ No se encontró el archivo: {archivo_gastos}')
        return
    
    try:
        df = pd.read_csv(archivo_gastos)
        
        # Buscar 'llancao' (case insensitive)
        filtro_llancao = df['Descripción'].str.contains('llancao', case=False, na=False)
        registros_llancao = df[filtro_llancao]
        
        if not registros_llancao.empty:
            print(f'✅ Encontrados {len(registros_llancao)} registros con "llancao":')
            print()
            for _, row in registros_llancao.iterrows():
                print(f'📅 Fecha: {row["Fecha"]}')
                print(f'💰 Monto: ${row["Monto"]:,.0f}')  
                print(f'📝 Descripción: {row["Descripción"]}')
                print(f'🏦 Origen: {row["Origen"]}')
                print(f'📂 Categoría: {row["Categoría_2"]}')
                print('-' * 40)
        else:
            print('❌ No se encontraron registros con "llancao"')
            print()
            print('💡 Probando búsquedas alternativas...')
            print()
            
            # Buscar 'hector'
            filtro_hector = df['Descripción'].str.contains('hector', case=False, na=False)
            registros_hector = df[filtro_hector]
            
            if not registros_hector.empty:
                print(f'✅ Encontrados {len(registros_hector)} registros con "hector":')
                for _, row in registros_hector.iterrows():
                    print(f'📅 {row["Fecha"]} | ${row["Monto"]:,.0f} | {row["Descripción"]} | 🏦 {row["Origen"]}')
                print()
            
            # Buscar 'traspaso'
            filtro_traspaso = df['Descripción'].str.contains('traspaso', case=False, na=False)
            registros_traspaso = df[filtro_traspaso]
            
            if not registros_traspaso.empty:
                print(f'✅ Encontrados {len(registros_traspaso)} registros con "traspaso":')
                for _, row in registros_traspaso.iterrows():
                    print(f'📅 {row["Fecha"]} | ${row["Monto"]:,.0f} | {row["Descripción"]} | 🏦 {row["Origen"]}')
                print()
            
            # Buscar 'TEF' (transferencias)
            filtro_tef = df['Descripción'].str.contains('TEF', case=False, na=False)
            registros_tef = df[filtro_tef]
            
            if not registros_tef.empty:
                print(f'✅ Encontrados {len(registros_tef)} registros con "TEF":')
                for _, row in registros_tef.iterrows():
                    print(f'📅 {row["Fecha"]} | ${row["Monto"]:,.0f} | {row["Descripción"]} | 🏦 {row["Origen"]}')
                    
    except Exception as e:
        print(f'❌ Error leyendo el archivo: {str(e)}')

if __name__ == '__main__':
    buscar_llancao() 