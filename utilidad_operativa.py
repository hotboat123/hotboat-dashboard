#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para generar la tabla "Utilidad operativa.csv"
Combina datos de:
- Gastos hotboat (filtrar por categoría 1 = "Costos de Marketing")
- Costos operativos
- Ingresos operativos

Estructura de salida:
- fecha, categoria, monto
- Categorías: "costo operativo", "ingreso operativo", "Costos de Marketing"
"""

import pandas as pd
import sys
import os
from datetime import datetime

# Forzar UTF-8 para evitar problemas con emojis en Windows
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

def cargar_gastos_marketing():
    """Cargar gastos filtrados por categoría 'Costos de Marketing'"""
    try:
        print("📊 Cargando gastos de marketing...")
        gastos = pd.read_csv('archivos_output/gastos hotboat.csv')
        
        # Filtrar por categoría 1 = "Costos de Marketing"
        gastos_marketing = gastos[gastos['Categoría 1'] == 'Costos de Marketing'].copy()
        
        # Seleccionar columnas necesarias y renombrar
        gastos_marketing = gastos_marketing[['Fecha', 'Monto']].copy()
        gastos_marketing['categoria'] = 'Costos de Marketing'
        gastos_marketing = gastos_marketing.rename(columns={'Fecha': 'fecha', 'Monto': 'monto'})
        
        print(f"✅ Gastos de marketing cargados: {len(gastos_marketing)} registros")
        return gastos_marketing
        
    except Exception as e:
        print(f"❌ Error cargando gastos de marketing: {e}")
        return pd.DataFrame()

def cargar_costos_fijos():
    """Cargar gastos filtrados por categoría 'Costos Fijos'"""
    try:
        print("📊 Cargando costos fijos...")
        gastos = pd.read_csv('archivos_output/gastos hotboat.csv')
        
        # Filtrar por categoría 1 = "Costos Fijos"
        costos_fijos = gastos[gastos['Categoría 1'] == 'Costos Fijos'].copy()
        
        # Seleccionar columnas necesarias y renombrar
        costos_fijos = costos_fijos[['Fecha', 'Monto']].copy()
        costos_fijos['categoria'] = 'costos fijos'
        costos_fijos = costos_fijos.rename(columns={'Fecha': 'fecha', 'Monto': 'monto'})
        
        print(f"✅ Costos fijos cargados: {len(costos_fijos)} registros")
        return costos_fijos
        
    except Exception as e:
        print(f"❌ Error cargando costos fijos: {e}")
        return pd.DataFrame()

def cargar_costos_variables():
    """Cargar gastos filtrados por categoría 'Costos Variables'"""
    try:
        print("📊 Cargando costos variables...")
        gastos = pd.read_csv('archivos_output/gastos hotboat.csv')
        
        # Filtrar por categoría 1 = "Costos Variables"
        costos_variables = gastos[gastos['Categoría 1'] == 'Costos Variables'].copy()
        
        # Seleccionar columnas necesarias y renombrar
        costos_variables = costos_variables[['Fecha', 'Monto']].copy()
        costos_variables['categoria'] = 'costos variables'
        costos_variables = costos_variables.rename(columns={'Fecha': 'fecha', 'Monto': 'monto'})
        
        print(f"✅ Costos variables cargados: {len(costos_variables)} registros")
        return costos_variables
        
    except Exception as e:
        print(f"❌ Error cargando costos variables: {e}")
        return pd.DataFrame()

def cargar_costos_operativos():
    """Cargar costos operativos"""
    try:
        print("📊 Cargando costos operativos...")
        costos = pd.read_csv('archivos_output/costos_operativos.csv')
        
        # Seleccionar columnas necesarias y renombrar
        costos_operativos = costos[['fecha', 'monto']].copy()
        costos_operativos['categoria'] = 'costo operativo'
        
        print(f"✅ Costos operativos cargados: {len(costos_operativos)} registros")
        return costos_operativos
        
    except Exception as e:
        print(f"❌ Error cargando costos operativos: {e}")
        return pd.DataFrame()

def cargar_ingresos_operativos():
    """Cargar ingresos operativos"""
    try:
        print("📊 Cargando ingresos operativos...")
        ingresos = pd.read_csv('archivos_output/ingresos_operativos.csv')
        
        # Seleccionar columnas necesarias y renombrar
        ingresos_operativos = ingresos[['fecha', 'monto']].copy()
        ingresos_operativos['categoria'] = 'ingreso operativo'
        
        print(f"✅ Ingresos operativos cargados: {len(ingresos_operativos)} registros")
        return ingresos_operativos
        
    except Exception as e:
        print(f"❌ Error cargando ingresos operativos: {e}")
        return pd.DataFrame()

def generar_utilidad_operativa():
    """Generar tabla consolidada de utilidad operativa"""
    print("🚀 Iniciando generación de tabla 'Utilidad operativa.csv'")
    print("=" * 60)
    
    # Cargar datos de todas las fuentes
    gastos_marketing = cargar_gastos_marketing()
    costos_fijos = cargar_costos_fijos()
    costos_variables = cargar_costos_variables()
    costos_operativos = cargar_costos_operativos()
    ingresos_operativos = cargar_ingresos_operativos()
    
    # Verificar que todos los archivos se cargaron correctamente
    if gastos_marketing.empty and costos_fijos.empty and costos_variables.empty and costos_operativos.empty and ingresos_operativos.empty:
        print("❌ No se pudieron cargar datos de ninguna fuente")
        return False
    
    # Combinar todos los datos
    print("\n🔗 Combinando datos...")
    utilidad_operativa = pd.concat([
        gastos_marketing,
        costos_fijos,
        costos_variables,
        costos_operativos,
        ingresos_operativos
    ], ignore_index=True)
    
    # Ordenar por fecha
    utilidad_operativa['fecha'] = pd.to_datetime(utilidad_operativa['fecha'])
    utilidad_operativa = utilidad_operativa.sort_values('fecha')
    
    # Reordenar columnas
    utilidad_operativa = utilidad_operativa[['fecha', 'categoria', 'monto']]
    
    # Guardar archivo
    output_file = 'archivos_output/Utilidad operativa.csv'
    utilidad_operativa.to_csv(output_file, index=False)
    
    # Mostrar resumen
    print("\n📈 RESUMEN DE UTILIDAD OPERATIVA")
    print("=" * 40)
    print(f"📅 Período: {utilidad_operativa['fecha'].min().strftime('%Y-%m-%d')} a {utilidad_operativa['fecha'].max().strftime('%Y-%m-%d')}")
    print(f"📊 Total registros: {len(utilidad_operativa):,}")
    
    # Estadísticas por categoría
    print("\n📋 Distribución por categoría:")
    for categoria in utilidad_operativa['categoria'].unique():
        count = len(utilidad_operativa[utilidad_operativa['categoria'] == categoria])
        total = utilidad_operativa[utilidad_operativa['categoria'] == categoria]['monto'].sum()
        print(f"  • {categoria}: {count:,} registros - ${total:,.0f}")
    
    # Totales generales
    total_ingresos = utilidad_operativa[utilidad_operativa['categoria'] == 'ingreso operativo']['monto'].sum()
    total_costos_operativos = utilidad_operativa[utilidad_operativa['categoria'] == 'costo operativo']['monto'].sum()
    total_marketing = utilidad_operativa[utilidad_operativa['categoria'] == 'Costos de Marketing']['monto'].sum()
    total_costos_fijos = utilidad_operativa[utilidad_operativa['categoria'] == 'costos fijos']['monto'].sum()
    total_costos_variables = utilidad_operativa[utilidad_operativa['categoria'] == 'costos variables']['monto'].sum()
    
    print(f"\n💰 TOTALES:")
    print(f"  • Ingresos operativos: ${total_ingresos:,.0f}")
    print(f"  • Costos operativos: ${total_costos_operativos:,.0f}")
    print(f"  • Costos de marketing: ${total_marketing:,.0f}")
    print(f"  • Costos fijos: ${total_costos_fijos:,.0f}")
    print(f"  • Costos variables: ${total_costos_variables:,.0f}")
    
    total_costos = total_costos_operativos + total_marketing + total_costos_fijos + total_costos_variables
    print(f"  • Total costos: ${total_costos:,.0f}")
    print(f"  • Utilidad neta: ${total_ingresos - total_costos:,.0f}")
    
    print(f"\n✅ Archivo generado: {output_file}")
    print(f"📁 Tamaño: {os.path.getsize(output_file):,} bytes")
    
    return True

def main():
    """Función principal"""
    try:
        # Verificar que estamos en el directorio correcto
        if not os.path.exists('archivos_output'):
            print("❌ Error: No se encontró el directorio 'archivos_output'")
            print("💡 Asegúrate de ejecutar este script desde el directorio raíz del proyecto")
            return False
        
        # Verificar que existen los archivos necesarios
        archivos_requeridos = [
            'archivos_output/gastos hotboat.csv',
            'archivos_output/costos_operativos.csv',
            'archivos_output/ingresos_operativos.csv'
        ]
        
        for archivo in archivos_requeridos:
            if not os.path.exists(archivo):
                print(f"❌ Error: No se encontró el archivo '{archivo}'")
                return False
        
        # Generar tabla de utilidad operativa
        success = generar_utilidad_operativa()
        
        if success:
            print("\n🎉 ¡Tabla 'Utilidad operativa.csv' generada exitosamente!")
        else:
            print("\n❌ Error generando la tabla de utilidad operativa")
        
        return success
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Proceso interrumpido por el usuario")
        return False
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    main() 