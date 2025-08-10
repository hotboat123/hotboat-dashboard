#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
💸 Costos de Marketing (Meta + Google) por día
=============================================

Lee los archivos de input de marketing diario y genera un consolidado por día.
Además, agrega estos costos a `archivos_output/Utilidad operativa.csv` bajo la
categoría 'costos de marketing'.

Entradas esperadas (carpeta):
  - archivos_input/archivos input marketing/gasto diario en meta.csv
  - archivos_input/archivos input marketing/gasto diario en google ads.csv

Salidas:
  - archivos_output/costos_marketing_diario.csv
  - Actualiza/crea: archivos_output/Utilidad operativa.csv

Uso:
  python costos_marketing.py
"""

import os
import sys
import pandas as pd
from typing import Optional


INPUT_DIR = os.path.join('archivos_input', 'archivos input marketing')
OUT_DIR = os.path.join('archivos_output')
OUT_COSTOS = os.path.join(OUT_DIR, 'costos_marketing_diario.csv')
UO_PATH = os.path.join(OUT_DIR, 'Utilidad operativa.csv')


def read_csv_auto(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        print(f"⚠️  No existe: {path}")
        return pd.DataFrame()
    try:
        df = pd.read_csv(path, sep=None, engine='python')
        return df
    except Exception:
        try:
            df = pd.read_csv(path)
            return df
        except Exception as e:
            print(f"❌ Error leyendo {path}: {str(e)}")
            return pd.DataFrame()


def find_date_column(columns: list[str]) -> Optional[str]:
    candidates = ['fecha', 'date', 'día', 'dia', 'day']
    lower = [c.lower().strip() for c in columns]
    for cand in candidates:
        if cand in lower:
            return columns[lower.index(cand)]
    # búsqueda parcial
    for i, c in enumerate(lower):
        if any(k in c for k in ['fecha', 'date', 'dia', 'day']):
            return columns[i]
    return None


def find_amount_column(columns: list[str]) -> Optional[str]:
    candidates = ['gasto', 'spend', 'cost', 'importe', 'monto']
    lower = [c.lower().strip() for c in columns]
    for cand in candidates:
        if cand in lower:
            return columns[lower.index(cand)]
    for i, c in enumerate(lower):
        if any(k in c for k in ['gasto', 'spend', 'cost', 'importe', 'monto']):
            return columns[i]
    return None


def preparar_diario(path: str, fuente: str) -> pd.DataFrame:
    df = read_csv_auto(path)
    if df.empty:
        return pd.DataFrame(columns=['fecha', 'fuente', 'monto'])

    date_col = find_date_column(list(df.columns))
    amt_col = find_amount_column(list(df.columns))
    if not date_col or not amt_col:
        print(f"⚠️  No se detectaron columnas fecha/monto en {path}")
        return pd.DataFrame(columns=['fecha', 'fuente', 'monto'])

    df_work = df[[date_col, amt_col]].copy()
    df_work.rename(columns={date_col: 'fecha', amt_col: 'monto'}, inplace=True)
    # Normalizaciones
    df_work['fecha'] = pd.to_datetime(df_work['fecha'], errors='coerce')
    # Reemplazar separadores y convertir
    if df_work['monto'].dtype == object:
        df_work['monto'] = (
            df_work['monto']
            .astype(str)
            .str.replace('.', '', regex=False)
            .str.replace(',', '.', regex=False)
        )
    df_work['monto'] = pd.to_numeric(df_work['monto'], errors='coerce')
    df_work = df_work.dropna(subset=['fecha', 'monto'])

    # Agrupar por día
    df_day = (
        df_work.groupby(df_work['fecha'].dt.date, as_index=False)['monto']
        .sum()
        .rename(columns={'fecha': 'fecha'})
    )
    df_day['fecha'] = pd.to_datetime(df_day['fecha'])
    df_day['fuente'] = fuente
    return df_day[['fecha', 'fuente', 'monto']]


def consolidar_costos_marketing() -> pd.DataFrame:
    meta_path = os.path.join(INPUT_DIR, 'gasto diario en meta.csv')
    google_path = os.path.join(INPUT_DIR, 'gasto diario en google ads.csv')

    df_meta = preparar_diario(meta_path, 'meta')
    df_google = preparar_diario(google_path, 'google')

    frames = [df for df in [df_meta, df_google] if not df.empty]
    if not frames:
        return pd.DataFrame(columns=['fecha', 'fuente', 'monto'])
    df = pd.concat(frames, ignore_index=True)
    # Consolidar por día (sumando fuentes)
    df_total = (
        df.groupby('fecha', as_index=False)['monto'].sum()
        .rename(columns={'monto': 'monto'})
    )
    return df_total


def agregar_a_utilidad_operativa(df_costos: pd.DataFrame) -> int:
    if df_costos.empty:
        print("ℹ️  No hay costos de marketing para agregar")
        return 0

    os.makedirs(OUT_DIR, exist_ok=True)
    # Leer UO existente (si está)
    if os.path.exists(UO_PATH):
        try:
            df_uo = pd.read_csv(UO_PATH)
        except Exception:
            df_uo = pd.DataFrame()
    else:
        df_uo = pd.DataFrame(columns=['fecha', 'categoria', 'monto'])

    # Estandarizar columnas
    if not df_uo.empty:
        # Normalizar fecha y monto en destino
        if 'fecha' in df_uo.columns:
            df_uo['fecha'] = pd.to_datetime(df_uo['fecha'], errors='coerce')
        if 'monto' in df_uo.columns:
            df_uo['monto'] = pd.to_numeric(df_uo['monto'], errors='coerce')
    else:
        df_uo = pd.DataFrame(columns=['fecha', 'categoria', 'monto'])

    # Preparar registros nuevos
    df_new = df_costos.copy()
    df_new = df_new.rename(columns={'fecha': 'fecha', 'monto': 'monto'})
    df_new['categoria'] = 'costos de marketing'
    df_new = df_new[['fecha', 'categoria', 'monto']]

    # Asegurar tipos
    df_new['fecha'] = pd.to_datetime(df_new['fecha'], errors='coerce')
    df_new['monto'] = pd.to_numeric(df_new['monto'], errors='coerce')
    df_new = df_new.dropna(subset=['fecha', 'monto'])

    # Concatenar y deduplicar por (fecha, categoria, monto)
    df_out = pd.concat([df_uo, df_new], ignore_index=True)
    if set(['fecha', 'categoria', 'monto']).issubset(df_out.columns):
        df_out.drop_duplicates(subset=['fecha', 'categoria', 'monto'], keep='first', inplace=True)
    df_out.sort_values('fecha', inplace=True)

    # Backup y guardar
    if os.path.exists(UO_PATH):
        backup_path = os.path.join(OUT_DIR, 'Utilidad operativa.backup.csv')
        try:
            df_uo.to_csv(backup_path, index=False)
            print(f"🗂️  Backup creado: {backup_path}")
        except Exception:
            pass

    df_out.to_csv(UO_PATH, index=False)
    print(f"✅ Utilidad operativa actualizada: {UO_PATH} ({len(df_out)} filas)")
    return len(df_new)


def main() -> bool:
    print("💸 Procesando costos de marketing diario (Meta + Google)…")
    df_costos = consolidar_costos_marketing()
    if df_costos.empty:
        print("⚠️  No se encontraron costos diarios en los archivos de input")
        return False

    os.makedirs(OUT_DIR, exist_ok=True)
    df_costos.to_csv(OUT_COSTOS, index=False)
    print(f"💾 Exportado: {OUT_COSTOS} ({len(df_costos)} filas)")

    agregados = agregar_a_utilidad_operativa(df_costos)
    print(f"➕ Registros agregados a Utilidad operativa: {agregados}")
    return True


if __name__ == '__main__':
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

