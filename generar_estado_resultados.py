#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📑 Generar Estado de Resultados (P&L) a partir de 'Utilidad operativa.csv'
=========================================================================

Entrada:
 - archivos_output/Utilidad operativa.csv  (columnas esperadas: fecha, categoria, monto)
 - archivos_output/gastos hotboat.csv      (para costos fijos: 'Fecha', 'Monto', 'Categoría 1')

Salida:
 - archivos_output/estado_resultados.csv           (resumen TOTAL)
 - archivos_output/estado_resultados_mensual.csv   (resumen por mes)

Uso:
    python generar_estado_resultados.py
"""

import os
import sys
import pandas as pd
from datetime import datetime


def leer_csv_seguro(ruta: str) -> pd.DataFrame:
    if not os.path.exists(ruta):
        print(f"❌ No existe: {ruta}")
        return pd.DataFrame()
    try:
        df = pd.read_csv(ruta)
        return df
    except Exception as e:
        print(f"❌ Error leyendo {ruta}: {str(e)}")
        return pd.DataFrame()


def normalizar_categoria_utilidad(cat: str) -> str:
    t = str(cat).strip().lower()
    if 'ingreso' in t:
        return 'ingreso operativo'
    if 'marketing' in t:
        return 'costos de marketing'
    if 'costo' in t:
        return 'costo operativo'
    return t


def preparar_utilidad_operativa(df_uo: pd.DataFrame) -> pd.DataFrame:
    if df_uo.empty:
        return pd.DataFrame(columns=['fecha', 'categoria', 'monto'])
    # Normalizar columnas esperadas
    cols = {c.lower().strip(): c for c in df_uo.columns}
    # Renombrar a estándar si hace falta
    ren = {}
    if 'fecha' not in cols:
        # Buscar variant
        for c in df_uo.columns:
            if c.lower().strip() in ('date', 'fechas'):
                ren[c] = 'fecha'
    if 'categoria' not in cols:
        for c in df_uo.columns:
            if c.lower().strip() in ('categoria', 'categoría', 'category'):
                ren[c] = 'categoria'
    if 'monto' not in cols:
        for c in df_uo.columns:
            if c.lower().strip() in ('monto', 'amount', 'valor'):
                ren[c] = 'monto'
    if ren:
        df_uo = df_uo.rename(columns=ren)

    # Coerciones
    df_uo['fecha'] = pd.to_datetime(df_uo['fecha'], errors='coerce')
    df_uo['monto'] = pd.to_numeric(df_uo['monto'], errors='coerce')
    df_uo['categoria'] = df_uo['categoria'].apply(normalizar_categoria_utilidad)
    df_uo = df_uo.dropna(subset=['fecha', 'monto'])
    return df_uo


def preparar_costos_fijos(df_gastos: pd.DataFrame) -> pd.DataFrame:
    if df_gastos.empty:
        return pd.DataFrame(columns=['Fecha', 'Monto', 'Categoría 1'])
    df_g = df_gastos.copy()
    # Normalizar nombres de columnas clave
    if 'Fecha' not in df_g.columns:
        for c in df_gastos.columns:
            if c.lower().strip() == 'fecha':
                df_g.rename(columns={c: 'Fecha'}, inplace=True)
                break
    if 'Monto' not in df_g.columns:
        for c in df_gastos.columns:
            if c.lower().strip() in ('monto', 'amount'):
                df_g.rename(columns={c: 'Monto'}, inplace=True)
                break
    if 'Categoría 1' not in df_g.columns:
        for c in df_gastos.columns:
            if c.lower().strip() in ('categoria 1', 'categoría 1', 'categoria_1'):
                df_g.rename(columns={c: 'Categoría 1'}, inplace=True)
                break
    df_g['Fecha'] = pd.to_datetime(df_g['Fecha'], errors='coerce')
    df_g['Monto'] = pd.to_numeric(df_g['Monto'], errors='coerce')
    df_g = df_g.dropna(subset=['Fecha', 'Monto'])
    mask_fijos = df_g['Categoría 1'].astype(str).str.strip().str.lower() == 'costos fijos'
    return df_g[mask_fijos].copy()


def calcular_pl(df_uo: pd.DataFrame, df_fijos: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if df_uo.empty and df_fijos.empty:
        columnas = [
            'periodo', 'Ingresos Operativos', 'Costo Operativo', 'Utilidad Bruta',
            'Costos de Marketing', 'Costos Fijos', 'Resultado Operativo', 'Resultado Final'
        ]
        return pd.DataFrame(columns=columnas), pd.DataFrame(columns=columnas)

    # Periodo YYYY-MM
    if not df_uo.empty:
        df_uo['periodo'] = df_uo['fecha'].dt.to_period('M').astype(str)
    # Períodos de fijos
    if not df_fijos.empty:
        df_fijos['periodo'] = pd.to_datetime(df_fijos['Fecha']).dt.to_period('M').astype(str)

    # Pivot utilidad operativa por periodo
    pivot = (
        df_uo
        .groupby(['periodo', 'categoria'], as_index=False)['monto']
        .sum()
        .pivot(index='periodo', columns='categoria', values='monto')
        .fillna(0.0)
    ) if not df_uo.empty else pd.DataFrame()

    # Asegurar columnas esperadas
    for col in ['ingreso operativo', 'costo operativo', 'costos de marketing']:
        if col not in pivot.columns:
            pivot[col] = 0.0
    pivot = pivot.reset_index()
    pivot = pivot[['periodo', 'ingreso operativo', 'costo operativo', 'costos de marketing']]

    # Sumar costos fijos por periodo
    fijos_periodo = (
        df_fijos.groupby('periodo', as_index=False)['Monto'].sum()
        .rename(columns={'Monto': 'Costos Fijos'})
    ) if not df_fijos.empty else pd.DataFrame(columns=['periodo', 'Costos Fijos'])

    df_month = pivot.fillna(0.0).merge(fijos_periodo, on='periodo', how='left')
    if 'Costos Fijos' not in df_month.columns:
        df_month['Costos Fijos'] = 0.0
    df_month = df_month.fillna(0.0)

    # Derivados
    df_month['Utilidad Bruta'] = df_month['ingreso operativo'] - df_month['costo operativo']
    df_month['Resultado Operativo'] = df_month['Utilidad Bruta'] - df_month['costos de marketing']
    df_month['Resultado Final'] = df_month['Resultado Operativo']  - df_month['Costos Fijos']

    # Renombrar a título
    df_month = df_month.rename(columns={
        'ingreso operativo': 'Ingresos Operativos',
        'costo operativo': 'Costo Operativo',
        'costos de marketing': 'Costos de Marketing',
    })

    # Orden columnas
    # Orden de presentación: Resultado Operativo antes de Costos Fijos
    df_month = df_month[[
        'periodo', 'Ingresos Operativos', 'Costo Operativo', 'Utilidad Bruta',
        'Costos de Marketing', 'Resultado Operativo', 'Costos Fijos', 'Resultado Final'
    ]]

    # Total
    total = df_month.drop(columns=['periodo']).sum().to_frame(name='TOTAL').T
    total.insert(0, 'periodo', 'TOTAL')

    return df_month, total


def guardar_csv(df: pd.DataFrame, ruta: str) -> None:
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    try:
        df.to_csv(ruta, index=False)
        print(f"💾 Exportado: {ruta} ({len(df)} filas)")
    except PermissionError:
        print(f"❌ No se puede escribir el archivo (permiso): {ruta}")
    except Exception as e:
        print(f"❌ Error guardando {ruta}: {str(e)}")


def main() -> bool:
    print("📑 Generando Estado de Resultados (P&L) …")

    ruta_uo = os.path.join('archivos_output', 'Utilidad operativa.csv')
    ruta_gastos = os.path.join('archivos_output', 'gastos hotboat.csv')
    df_uo_raw = leer_csv_seguro(ruta_uo)
    df_gastos_raw = leer_csv_seguro(ruta_gastos)
    df_uo = preparar_utilidad_operativa(df_uo_raw)
    df_fijos = preparar_costos_fijos(df_gastos_raw)
    df_mensual, df_total = calcular_pl(df_uo, df_fijos)

    out_mensual = os.path.join('archivos_output', 'estado_resultados_mensual.csv')
    out_total = os.path.join('archivos_output', 'estado_resultados.csv')

    guardar_csv(df_mensual, out_mensual)
    guardar_csv(df_total, out_total)

    print("✅ Estado de Resultados generado con éxito")
    return True


if __name__ == '__main__':
    # UTF-8 para emojis
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

    try:
        ok = main()
        sys.exit(0 if ok else 1)
    except KeyboardInterrupt:
        print("\n🛑 Interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        sys.exit(1)

