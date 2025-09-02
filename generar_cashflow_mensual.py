import os
import sys
import pandas as pd
from datetime import datetime


OUTPUT_DIR = 'archivos_output'
PATH_CC = os.path.join(OUTPUT_DIR, 'cuenta_corriente_consolidado.csv')
PATH_ABONOS = os.path.join(OUTPUT_DIR, 'abonos hotboat cta cte.csv')
PATH_GASTOS = os.path.join(OUTPUT_DIR, 'gastos hotboat.csv')
PATH_CASHFLOW = os.path.join(OUTPUT_DIR, 'cashflow_mensual.csv')
PATH_CASHFLOW_FORMAT = os.path.join(OUTPUT_DIR, 'cashflow_mensual_formato.csv')


def read_csv_safe(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        print(f"❌ Archivo no encontrado: {path}", file=sys.stderr)
        return pd.DataFrame()
    try:
        df = pd.read_csv(path)
        return df
    except Exception as e:
        print(f"❌ Error leyendo {path}: {str(e)}", file=sys.stderr)
        return pd.DataFrame()


def normalize_fecha(df: pd.DataFrame, col: str = 'Fecha') -> pd.DataFrame:
    if df is None or df.empty or col not in df.columns:
        return df
    df = df.copy()
    try:
        df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=True)
    except Exception:
        pass
    return df


def month_key(series: pd.Series) -> pd.Series:
    return series.dt.to_period('M').astype(str)


def ensure_month(df: pd.DataFrame, fecha_col: str = 'Fecha') -> pd.Series:
    """
    Devuelve una serie 'Mes' robusta en formato 'YYYY-MM' desde la columna de fecha.
    Intenta: datetime -> period M; parse ISO; parse dayfirst; fallback a slice 'YYYY-MM'.
    """
    if df is None or df.empty or fecha_col not in df.columns:
        return pd.Series(dtype=str)

    serie = df[fecha_col]
    # Si ya es datetime
    if pd.api.types.is_datetime64_any_dtype(serie):
        return month_key(serie)

    # Intento 1: ISO
    parsed = pd.to_datetime(serie, errors='coerce')
    if parsed.notna().any():
        return month_key(parsed)

    # Intento 2: dayfirst (dd/mm/yyyy)
    parsed2 = pd.to_datetime(serie, errors='coerce', dayfirst=True)
    if parsed2.notna().any():
        return month_key(parsed2)

    # Fallback: extraer 'YYYY-MM' del string si está presente
    s = serie.astype(str).str.strip()
    mask_iso = s.str.match(r'^\d{4}-\d{2}-\d{2}')
    if mask_iso.any():
        return s.str.slice(0, 7)

    # Último recurso: intentar dd/mm/yyyy y formatear
    parsed3 = pd.to_datetime(s, errors='coerce', dayfirst=True)
    out = pd.Series(pd.NA, index=df.index, dtype='object')
    ok = parsed3.notna()
    out.loc[ok] = parsed3.dt.strftime('%Y-%m')
    return out.astype(str)


def compute_cc_balances(df_cc: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula beginning y ending balance mensual desde cuenta corriente consolidada.
    Requiere columna 'Saldo (CLP)'. Si no existe, deja NaN.
    Estrategia:
      - ending_balance(m)  = último 'Saldo (CLP)' del mes m
      - beginning_balance(m) = ending_balance(m-1) (para el primer mes queda NaN)
    """
    if df_cc is None or df_cc.empty:
        return pd.DataFrame(columns=['Mes', 'Beginning_Balance', 'Ending_Balance'])

    df_cc = normalize_fecha(df_cc, 'Fecha')
    if 'Saldo (CLP)' not in df_cc.columns:
        # Sin saldo no podemos inferir balances absolutos
        grp = df_cc.groupby(month_key(df_cc['Fecha']), dropna=True)
        return pd.DataFrame({
            'Mes': list(grp.groups.keys()),
            'Beginning_Balance': [pd.NA] * len(grp),
            'Ending_Balance': [pd.NA] * len(grp),
        })

    df_cc = df_cc.sort_values('Fecha').reset_index(drop=True)
    df_cc['Mes'] = month_key(df_cc['Fecha'])
    ending = df_cc.groupby('Mes', as_index=False)['Saldo (CLP)'].last().rename(columns={'Saldo (CLP)': 'Ending_Balance'})
    ending = ending.sort_values('Mes')
    ending['Beginning_Balance'] = ending['Ending_Balance'].shift(1)
    ending = ending[['Mes', 'Beginning_Balance', 'Ending_Balance']]
    return ending


def sum_abonos_by_tipo(df_abonos: pd.DataFrame) -> pd.DataFrame:
    """
    Suma abonos por Categoría 1: 'Ingreso operativo', 'Inversión', 'otros'.
    """
    if df_abonos is None or df_abonos.empty:
        return pd.DataFrame(columns=['Mes', 'Ingresos_Operativos', 'Inversiones', 'Otros_Ingresos'])

    df = df_abonos.copy()
    # Mes robusto
    df['Mes'] = ensure_month(df, 'Fecha')
    if 'Monto' in df.columns:
        df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce')
    else:
        df['Monto'] = 0

    # Normalizar cat1
    cat1 = df.get('Categoría 1') if 'Categoría 1' in df.columns else df.get('Categoria 1')
    if cat1 is None:
        df['Categoría 1'] = 'otros'
    else:
        df['Categoría 1'] = cat1.astype(str).str.strip().str.lower()

    def tipo_ingreso(v: str) -> str:
        v = str(v).strip().lower()
        if 'operativ' in v:  # ingreso operativo
            return 'Ingresos_Operativos'
        if 'invers' in v:    # inversión
            return 'Inversiones'
        return 'Otros_Ingresos'

    df['tipo'] = df['Categoría 1'].apply(tipo_ingreso)
    tabla = df.pivot_table(index='Mes', columns='tipo', values='Monto', aggfunc='sum', fill_value=0)
    tabla = tabla.reset_index()
    for col in ['Ingresos_Operativos', 'Inversiones', 'Otros_Ingresos']:
        if col not in tabla.columns:
            tabla[col] = 0.0
    return tabla[['Mes', 'Ingresos_Operativos', 'Inversiones', 'Otros_Ingresos']]


def sum_gastos_by_cat1(df_gastos: pd.DataFrame) -> pd.DataFrame:
    """
    Suma gastos por Categoría 1: fijos, variables, marketing, capex.
    """
    if df_gastos is None or df_gastos.empty:
        return pd.DataFrame(columns=['Mes', 'Costos_Fijos', 'Costos_Variables', 'Marketing', 'CAPEX'])

    df = df_gastos.copy()
    # Mes robusto
    df['Mes'] = ensure_month(df, 'Fecha')
    if 'Monto' in df.columns:
        df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce')
    else:
        df['Monto'] = 0

    cat1 = df.get('Categoría 1') if 'Categoría 1' in df.columns else df.get('Categoria 1')
    if cat1 is None:
        df['Categoría 1'] = ''
    else:
        df['Categoría 1'] = cat1.astype(str).str.strip().str.lower()

    def map_gasto(v: str) -> str:
        v = str(v).strip().lower()
        if 'fijo' in v:
            return 'Costos_Fijos'
        if 'variable' in v:
            return 'Costos_Variables'
        if 'marketing' in v:
            return 'Marketing'
        if 'capex' in v or 'activo' in v:
            return 'CAPEX'
        return 'Otros_Gastos'

    df['tipo_gasto'] = df['Categoría 1'].apply(map_gasto)
    tabla = df.pivot_table(index='Mes', columns='tipo_gasto', values='Monto', aggfunc='sum', fill_value=0)
    tabla = tabla.reset_index()
    for col in ['Costos_Fijos', 'Costos_Variables', 'Marketing', 'CAPEX']:
        if col not in tabla.columns:
            tabla[col] = 0.0
    return tabla[['Mes', 'Costos_Fijos', 'Costos_Variables', 'Marketing', 'CAPEX']]


def build_cashflow(cc_bal: pd.DataFrame, abonos: pd.DataFrame, gastos: pd.DataFrame) -> pd.DataFrame:
    # Merge base por Mes
    df = pd.DataFrame({'Mes': sorted(set(cc_bal.get('Mes', pd.Series(dtype=str)).tolist() +
                                      abonos.get('Mes', pd.Series(dtype=str)).tolist() +
                                      gastos.get('Mes', pd.Series(dtype=str)).tolist()))})
    if 'Mes' not in df.columns:
        return pd.DataFrame()

    df = df.merge(cc_bal, on='Mes', how='left')
    df = df.merge(abonos, on='Mes', how='left')
    df = df.merge(gastos, on='Mes', how='left')

    # Rellenar NaN con 0 en montos
    monto_cols = ['Ingresos_Operativos', 'Inversiones', 'Otros_Ingresos', 'Costos_Fijos', 'Costos_Variables', 'Marketing', 'CAPEX']
    for c in monto_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0.0)
        else:
            df[c] = 0.0

    df['Total_Ingresos'] = df['Ingresos_Operativos'] + df['Inversiones'] + df['Otros_Ingresos']
    df['Total_Gastos'] = df['Costos_Fijos'] + df['Costos_Variables'] + df['Marketing'] + df['CAPEX']
    df['Net_Cash_Flow'] = df['Total_Ingresos'] - df['Total_Gastos']

    # Ordenar por Mes cronológicamente
    try:
        orden = pd.to_datetime(df['Mes'] + '-01')
        df = df.iloc[orden.argsort()].reset_index(drop=True)
    except Exception:
        pass

    # Calcular Ending_Balance_Flow si hay Beginning_Balance
    if 'Beginning_Balance' in df.columns:
        df['Ending_Balance_Flow'] = (pd.to_numeric(df['Beginning_Balance'], errors='coerce') + df['Net_Cash_Flow']).round(2)
    else:
        df['Ending_Balance_Flow'] = pd.NA

    cols_order = [
        'Mes',
        'Beginning_Balance', 'Ending_Balance',
        'Ingresos_Operativos', 'Inversiones', 'Otros_Ingresos', 'Total_Ingresos',
        'Costos_Fijos', 'Costos_Variables', 'Marketing', 'CAPEX', 'Total_Gastos',
        'Net_Cash_Flow', 'Ending_Balance_Flow'
    ]
    final_cols = [c for c in cols_order if c in df.columns]
    return df[final_cols]


def _series_from(df: pd.DataFrame, key_col: str, value_col: str) -> dict:
    if df is None or df.empty or key_col not in df.columns or value_col not in df.columns:
        return {}
    s = df.set_index(key_col)[value_col]
    try:
        s = pd.to_numeric(s, errors='coerce')
    except Exception:
        pass
    return s.fillna(0).to_dict()


def _sorted_months(*dfs: pd.DataFrame) -> list:
    meses = set()
    for df in dfs:
        if isinstance(df, pd.DataFrame) and not df.empty and 'Mes' in df.columns:
            meses.update(df['Mes'].dropna().astype(str).tolist())
    if not meses:
        return []
    try:
        return sorted(list(meses), key=lambda m: pd.to_datetime(m + '-01'))
    except Exception:
        return sorted(list(meses))


def build_cashflow_statement_formatted(cc_bal: pd.DataFrame, abonos: pd.DataFrame, gastos: pd.DataFrame) -> pd.DataFrame:
    """
    Construye un estado de flujo de caja mensual en formato de filas=partidas y columnas=meses,
    separando Operating (OPEX), Investing (CAPEX) y Financing, manteniendo el orden del ejemplo.
    """
    meses = _sorted_months(cc_bal, abonos, gastos)
    if not meses:
        return pd.DataFrame()

    # Series por mes
    beg = _series_from(cc_bal, 'Mes', 'Beginning_Balance')
    end = _series_from(cc_bal, 'Mes', 'Ending_Balance')

    ingresos_op = _series_from(abonos, 'Mes', 'Ingresos_Operativos')
    inversiones = _series_from(abonos, 'Mes', 'Inversiones')
    otros_ing = _series_from(abonos, 'Mes', 'Otros_Ingresos')

    fijos = _series_from(gastos, 'Mes', 'Costos_Fijos')
    variables = _series_from(gastos, 'Mes', 'Costos_Variables')
    marketing = _series_from(gastos, 'Mes', 'Marketing')
    capex = _series_from(gastos, 'Mes', 'CAPEX')

    # Helpers para obtener valor por mes con default 0
    g = lambda d, m: float(d.get(m, 0.0))
    gb = lambda m: beg.get(m, pd.NA)
    ge = lambda m: end.get(m, pd.NA)

    # Precalcular subtotales por mes
    net_op = {m: g(ingresos_op, m) - (g(fijos, m) + g(variables, m) + g(marketing, m)) for m in meses}
    net_inv = {m: -g(capex, m) for m in meses}
    net_fin = {m: g(inversiones, m) + g(otros_ing, m) for m in meses}
    net_change = {m: net_op[m] + net_inv[m] + net_fin[m] for m in meses}

    # Ending balance por flujo (si no hay ending real, usar beginning + net_change)
    ending_flow = {}
    for m in meses:
        if pd.notna(ge(m)):
            ending_flow[m] = ge(m)
        elif pd.notna(gb(m)):
            try:
                ending_flow[m] = float(gb(m)) + net_change[m]
            except Exception:
                ending_flow[m] = pd.NA
        else:
            ending_flow[m] = pd.NA

    # Armar tabla
    filas = [
        ('Beginning Balance', lambda m: gb(m)),
        ('Operating Activities', None),
        ('Cash Receipts from Customers', lambda m: g(ingresos_op, m)),
        ('Cash Paid - Fixed Costs', lambda m: -g(fijos, m)),
        ('Cash Paid - Variable Costs', lambda m: -g(variables, m)),
        ('Cash Paid - Marketing', lambda m: -g(marketing, m)),
        ('Net Cash Flow from Operating Activities', lambda m: net_op[m]),
        ('Investing Activities', None),
        ('Purchase of Property, Plant & Equipment', lambda m: -g(capex, m)),
        ('Net Cash Flow from Investing Activities', lambda m: net_inv[m]),
        ('Financing Activities', None),
        ('Issuance of Common Stock', lambda m: g(inversiones, m)),
        ('Other Financing Inflows', lambda m: g(otros_ing, m)),
        ('Net Cash Flow from Financing Activities', lambda m: net_fin[m]),
        ('Net Cash Increase/Decrease in Cash', lambda m: net_change[m]),
        ('Ending Cash Balance', lambda m: ending_flow[m]),
    ]

    data = {'Particulars': []}
    for m in meses:
        data[m] = []

    for label, fn in filas:
        data['Particulars'].append(label)
        for m in meses:
            if fn is None:
                data[m].append('')  # filas de título de sección
            else:
                data[m].append(fn(m))

    df_stmt = pd.DataFrame(data)
    return df_stmt


def main():
    print("📊 Generando cashflow mensual...")

    df_cc = read_csv_safe(PATH_CC)
    df_abonos = read_csv_safe(PATH_ABONOS)
    df_gastos = read_csv_safe(PATH_GASTOS)

    balances = compute_cc_balances(df_cc)
    abonos_m = sum_abonos_by_tipo(df_abonos)
    gastos_m = sum_gastos_by_cat1(df_gastos)

    cashflow = build_cashflow(balances, abonos_m, gastos_m)
    if cashflow is None or cashflow.empty:
        print("⚠️ No se pudo construir el cashflow mensual (datos insuficientes)")
        return

    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        cashflow.to_csv(PATH_CASHFLOW, index=False)
        print(f"✅ Cashflow mensual exportado a: {PATH_CASHFLOW}")
    except Exception as e:
        print(f"❌ Error exportando cashflow: {str(e)}", file=sys.stderr)

    # Construir formato tipo estado de flujo (filas=partidas, columnas=meses)
    stmt = build_cashflow_statement_formatted(balances, abonos_m, gastos_m)
    if stmt is None or stmt.empty:
        print("⚠️ No se pudo construir el cashflow en formato de estado (datos insuficientes)")
        return
    try:
        stmt.to_csv(PATH_CASHFLOW_FORMAT, index=False)
        print(f"✅ Cashflow mensual (formato estado) exportado a: {PATH_CASHFLOW_FORMAT}")
    except Exception as e:
        print(f"❌ Error exportando cashflow formato: {str(e)}", file=sys.stderr)


if __name__ == '__main__':
    main()


