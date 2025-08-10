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

# Configurar UTF-8 de forma segura (especialmente en Windows/PowerShell)
try:
    # Disponible en Python 3.7+
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    # Si no se puede reconfigurar, continuar sin forzar (evita romper stdout)
    pass

def cargar_gastos_marketing():
    """Cargar gastos de marketing desde archivos diarios de Meta y Google Ads.

    Lee:
      - archivos_input/archivos input marketing/costo diario en meta.csv
      - archivos_input/archivos input marketing/costo diario en google ads.csv

    Devuelve DataFrame con columnas: fecha, categoria, categoria_2, descripcion, monto
    """
    def read_csv_auto(path: str) -> pd.DataFrame:
        try:
            # Para archivos de Google Ads, saltar las 2 filas de encabezado extra
            if 'google' in os.path.basename(path).lower():
                return pd.read_csv(path, sep=None, engine='python', skiprows=2)
            else:
                return pd.read_csv(path, sep=None, engine='python')
        except Exception:
            try:
                # Intentar con skiprows=2 para Google Ads
                if 'google' in os.path.basename(path).lower():
                    return pd.read_csv(path, skiprows=2)
                else:
                    return pd.read_csv(path)
            except Exception:
                return pd.DataFrame()

    def detect_col(columns: list, candidates: list) -> str:
        lower = [c.lower().strip() for c in columns]
        for cand in candidates:
            if cand in lower:
                return columns[lower.index(cand)]
        for i, c in enumerate(lower):
            if any(k in c for k in candidates):
                return columns[i]
        return ''

    def preparar(path: str, fuente: str) -> pd.DataFrame:
        df = read_csv_auto(path)
        if df.empty:
            return pd.DataFrame(columns=['fecha', 'monto'])
        fecha_col = detect_col(list(df.columns), ['fecha', 'date', 'dia', 'día', 'day', 'date_start', 'reporting starts', 'reporting_start'])
        monto_col = detect_col(list(df.columns), [
            'gasto','costo','coste','spend','spent','amount','amount spent','spent (clp)','importe','importe gastado',
            'monto','monto gastado','ad spend','cost'
        ])
        if not fecha_col or not monto_col:
            return pd.DataFrame(columns=['fecha', 'monto'])
        d = df[[fecha_col, monto_col]].copy()
        d.rename(columns={fecha_col: 'fecha', monto_col: 'monto'}, inplace=True)
        d['fecha'] = pd.to_datetime(d['fecha'], errors='coerce')
        if d['monto'].dtype == object:
            # Normalizar valores monetarios: quitar símbolos y miles, preservar decimales
            s = d['monto'].astype(str).str.replace('\u202f', '', regex=True)
            s = s.str.replace('$', '', regex=False).str.replace('CLP', '', regex=False).str.strip()
            # Caso latino: 1.234,56 -> 1234.56
            s_lat = s.str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
            d['monto'] = pd.to_numeric(s_lat, errors='coerce')
        # Debug: columnas detectadas y primeras filas válidas
        try:
            print(f"   🔎 {fuente}: archivo='{os.path.basename(path)}', fecha_col='{fecha_col}', monto_col='{monto_col}'")
        except Exception:
            pass
        d['monto'] = pd.to_numeric(d['monto'], errors='coerce')
        d = d.dropna(subset=['fecha', 'monto'])
        before = len(d)
        # Normalizar fecha al día y agrupar por nombre de columna para mayor compatibilidad
        d['fecha'] = pd.to_datetime(d['fecha'], errors='coerce').dt.floor('D')
        d = d.groupby('fecha', as_index=False)['monto'].sum()
        d['categoria'] = 'Costos de Marketing'
        d['categoria_2'] = 'Meta' if fuente == 'meta' else 'Google Ads'
        d['descripcion'] = f'Gasto diario {"Meta" if fuente == "meta" else "Google Ads"}'
        try:
            print(f"   ✅ {fuente}: filas válidas={before}, días agregados={len(d)}, total=${d['monto'].sum():,.0f}")
        except Exception:
            pass
        return d

    try:
        print("📊 Cargando gastos de marketing (Meta + Google Ads) desde archivos diarios…")
        base_dir = os.path.join('archivos_input', 'archivos input marketing')
        # Descubrir archivos por nombre si cambiaron (soporta 'gasto diario' y 'costo diario')
        meta_defaults = [
            os.path.join(base_dir, 'gasto diario en meta.csv'),
            os.path.join(base_dir, 'costo diario en meta.csv'),
        ]
        google_defaults = [
            os.path.join(base_dir, 'gasto diario en google ads.csv'),
            os.path.join(base_dir, 'costo diario en google ads.csv'),
        ]
        meta_default = next((p for p in meta_defaults if os.path.exists(p)), '')
        google_default = next((p for p in google_defaults if os.path.exists(p)), '')
        meta_path = meta_default if os.path.exists(meta_default) else ''
        google_path = google_default if os.path.exists(google_default) else ''
        try:
            files = [f for f in os.listdir(base_dir) if f.lower().endswith('.csv')]
        except Exception:
            files = []
        if not meta_path:
            for f in files:
                fl = f.lower()
                if 'meta' in fl or 'facebook' in fl:
                    meta_path = os.path.join(base_dir, f)
                    break
        if not google_path:
            for f in files:
                fl = f.lower()
                if 'google' in fl:
                    google_path = os.path.join(base_dir, f)
                    break

        df_meta = preparar(meta_path, 'meta') if meta_path else pd.DataFrame()
        df_google = preparar(google_path, 'google') if google_path else pd.DataFrame()
        frames = [df for df in [df_meta, df_google] if not df.empty]
        if not frames:
            try:
                files = os.listdir(base_dir)
                print(f"⚠️  No se encontraron gastos de marketing diarios. Archivos en carpeta: {files}")
            except Exception:
                print("⚠️  No se encontraron gastos de marketing diarios y no se pudo listar la carpeta de input")
            return pd.DataFrame(columns=['fecha', 'categoria', 'categoria_2', 'descripcion', 'monto'])

        gastos_marketing = pd.concat(frames, ignore_index=True)
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
        columnas_necesarias = ['Fecha', 'Monto', 'Descripción']
        if 'Categoría_2' in costos_fijos.columns:
            columnas_necesarias.append('Categoría_2')
        
        costos_fijos = costos_fijos[columnas_necesarias].copy()
        costos_fijos['categoria'] = 'costos fijos'
        costos_fijos['categoria_2'] = costos_fijos.get('Categoría_2', 'Sin subcategoría')
        costos_fijos['descripcion'] = costos_fijos.get('Descripción', 'Costo fijo')
        costos_fijos = costos_fijos.rename(columns={'Fecha': 'fecha', 'Monto': 'monto'})
        
        # Convertir fecha a datetime si no lo está
        costos_fijos['fecha'] = pd.to_datetime(costos_fijos['fecha'])
        
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
        columnas_necesarias = ['Fecha', 'Monto', 'Descripción']
        if 'Categoría_2' in costos_variables.columns:
            columnas_necesarias.append('Categoría_2')
        
        costos_variables = costos_variables[columnas_necesarias].copy()
        costos_variables['categoria'] = 'costos variables'
        costos_variables['categoria_2'] = costos_variables.get('Categoría_2', 'Sin subcategoría')
        costos_variables['descripcion'] = costos_variables.get('Descripción', 'Costo variable')
        costos_variables = costos_variables.rename(columns={'Fecha': 'fecha', 'Monto': 'monto'})
        
        # Convertir fecha a datetime si no lo está
        costos_variables['fecha'] = pd.to_datetime(costos_variables['fecha'])
        
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
        costos_operativos['categoria_2'] = 'Por reserva'
        costos_operativos['descripcion'] = 'Costo operativo por reserva'
        
        # Convertir fecha a datetime si no lo está
        costos_operativos['fecha'] = pd.to_datetime(costos_operativos['fecha'])
        
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
        ingresos_operativos['categoria_2'] = 'Reservas'
        ingresos_operativos['descripcion'] = 'Ingreso por reserva'
        
        # Convertir fecha a datetime si no lo está
        ingresos_operativos['fecha'] = pd.to_datetime(ingresos_operativos['fecha'])
        
        print(f"✅ Ingresos operativos cargados: {len(ingresos_operativos)} registros")
        return ingresos_operativos
        
    except Exception as e:
        print(f"❌ Error cargando ingresos operativos: {e}")
        return pd.DataFrame()

def cargar_todos_gastos():
    """Cargar TODOS los gastos de gastos hotboat.csv preservando categorías originales"""
    try:
        print("📊 Cargando todos los gastos...")
        gastos = pd.read_csv('archivos_output/gastos hotboat.csv')
        
        # Seleccionar columnas necesarias y renombrar
        columnas_necesarias = ['Fecha', 'Monto', 'Descripción']
        if 'Categoría_2' in gastos.columns:
            columnas_necesarias.append('Categoría_2')
        if 'Categoría 1' in gastos.columns:
            columnas_necesarias.append('Categoría 1')
        
        gastos_todos = gastos[columnas_necesarias].copy()
        gastos_todos['categoria'] = gastos_todos.get('Categoría 1', 'Sin categoría')
        gastos_todos['categoria_2'] = gastos_todos.get('Categoría_2', 'Sin subcategoría')
        gastos_todos['descripcion'] = gastos_todos.get('Descripción', 'Gasto')
        gastos_todos = gastos_todos.rename(columns={'Fecha': 'fecha', 'Monto': 'monto'})
        
        # Convertir fecha a datetime si no lo está
        gastos_todos['fecha'] = pd.to_datetime(gastos_todos['fecha'])
        
        print(f"✅ Todos los gastos cargados: {len(gastos_todos)} registros")
        return gastos_todos
        
    except Exception as e:
        print(f"❌ Error cargando todos los gastos: {e}")
        return pd.DataFrame()

def cargar_todos_abonos():
    """Cargar TODOS los abonos de abonos hotboat.csv"""
    try:
        print("📊 Cargando todos los abonos...")
        abonos = pd.read_csv('archivos_output/abonos hotboat.csv')
        
        # Seleccionar columnas necesarias y renombrar
        abonos_todos = abonos[['Fecha', 'Monto', 'Descripción']].copy()
        abonos_todos['categoria'] = 'abonos'
        abonos_todos['categoria_2'] = 'Abonos bancarios'
        abonos_todos['descripcion'] = abonos_todos.get('Descripción', 'Abono')
        abonos_todos = abonos_todos.rename(columns={'Fecha': 'fecha', 'Monto': 'monto'})
        
        # Convertir fecha a datetime si no lo está
        abonos_todos['fecha'] = pd.to_datetime(abonos_todos['fecha'])
        
        print(f"✅ Todos los abonos cargados: {len(abonos_todos)} registros")
        return abonos_todos
        
    except Exception as e:
        print(f"❌ Error cargando todos los abonos: {e}")
        return pd.DataFrame()

def generar_utilidad_operativa():
    """Generar tabla consolidada de utilidad operativa"""
    print("🚀 Iniciando generación de tabla 'Utilidad operativa.csv'")
    print("=" * 60)
    
    # Cargar datos de todas las fuentes
    gastos_marketing = cargar_gastos_marketing()
    costos_fijos = cargar_costos_fijos()
    # costos_variables = cargar_costos_variables()
    costos_operativos = cargar_costos_operativos()
    ingresos_operativos = cargar_ingresos_operativos()
    # gastos_todos = cargar_todos_gastos()
    # abonos_todos = cargar_todos_abonos()
    
    # Verificar que todos los archivos se cargaron correctamente
    if gastos_marketing.empty and costos_fijos.empty and costos_operativos.empty and ingresos_operativos.empty:
    # if gastos_marketing.empty and costos_fijos.empty and costos_variables.empty and costos_operativos.empty and ingresos_operativos.empty and gastos_todos.empty and abonos_todos.empty:
        print("❌ No se pudieron cargar datos de ninguna fuente")
        return False
    
    # Combinar todos los datos
    print("\n🔗 Combinando datos...")
    utilidad_operativa = pd.concat([
        gastos_marketing,
        costos_fijos,
        #costos_variables,
        costos_operativos,
        ingresos_operativos,
        #gastos_todos,
        #abonos_todos
    ], ignore_index=True)
    
    # Ordenar por fecha (ya están en formato datetime)
    utilidad_operativa = utilidad_operativa.sort_values('fecha')
    
    # Reordenar columnas
    utilidad_operativa = utilidad_operativa[['fecha', 'categoria', 'categoria_2', 'descripcion', 'monto']]
    
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
    total_gastos = utilidad_operativa[utilidad_operativa['categoria'] == 'gastos']['monto'].sum()
    total_abonos = utilidad_operativa[utilidad_operativa['categoria'] == 'abonos']['monto'].sum()
    
    print(f"\n💰 TOTALES:")
    print(f"  • Ingresos operativos: ${total_ingresos:,.0f}")
    print(f"  • Abonos bancarios: ${total_abonos:,.0f}")
    print(f"  • Total ingresos: ${total_ingresos + total_abonos:,.0f}")
    print(f"  • Costos operativos: ${total_costos_operativos:,.0f}")
    print(f"  • Costos de marketing: ${total_marketing:,.0f}")
    print(f"  • Costos fijos: ${total_costos_fijos:,.0f}")
    print(f"  • Costos variables: ${total_costos_variables:,.0f}")
    print(f"  • Gastos totales: ${total_gastos:,.0f}")
    
    total_costos = total_costos_operativos + total_marketing + total_costos_fijos + total_costos_variables + total_gastos
    total_ingresos_totales = total_ingresos + total_abonos
    print(f"  • Total costos: ${total_costos:,.0f}")
    print(f"  • Utilidad neta: ${total_ingresos_totales - total_costos:,.0f}")
    
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