#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera archivos simulados y un consolidado de "utilidad operativa simulacion".

Salida en archivos_output/:
- ingresos_operativos_simulacion.csv (fecha,email,id_reserva,descripcion,monto)
- costos_operativos_simulacion.csv  (fecha,email,id_reserva,descripcion,monto)
- Utilidad operativa simulacion.csv (fecha,categoria,categoria_2,descripcion,monto)

Parámetros en inputs_simulacion.py
"""

import os
import sys
from datetime import datetime
from calendar import monthrange
import pandas as pd

# Asegurar UTF-8 en Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

try:
    import inputs_simulacion as cfg
except Exception as e:
    print(f"❌ No se pudo importar inputs_simulacion.py: {e}")
    raise


def asegurar_directorio_salida() -> str:
    out_dir = os.path.join('archivos_output')
    os.makedirs(out_dir, exist_ok=True)
    return out_dir


def generar_fechas_para_mes(yyyy_mm: str, cantidad: int) -> list:
    """Distribuye `cantidad` fechas de reservas dentro del mes dado (YYYY-MM).
    Usa días espaciados y hora fija 12:00 para simplicidad.
    """
    year, month = map(int, yyyy_mm.split('-'))
    last_day = monthrange(year, month)[1]
    if cantidad <= 0:
        return []
    # Espaciado uniforme por día; si cantidad > días, agrupar en días consecutivos
    step = max(1, last_day // max(1, min(last_day, cantidad)))
    days = []
    d = 1
    for _ in range(cantidad):
        days.append(min(d, last_day))
        d += step
        if d > last_day:
            d = (d - last_day)
            if d < 1:
                d = 1
    fechas = [datetime(year, month, day, 12, 0, 0) for day in sorted(days)]
    # Si hay duplicados por redondeo, ajustar minutos incremental
    if len(set(fechas)) < len(fechas):
        acc = {}
        ajustadas = []
        for f in fechas:
            count = acc.get(f, 0)
            ajustadas.append(f.replace(minute=(f.minute + count) % 60))
            acc[f] = count + 5
        return ajustadas
    return fechas


def construir_ingresos_y_costos_simulados() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    registros_ingresos = []
    registros_costos_op = []
    registros_marketing = []
    registros_costos_fijos = []

    id_counter = cfg.id_reserva_base

    for yyyy_mm, demanda in (cfg.demanda_por_mes or {}).items():
        fechas = generar_fechas_para_mes(yyyy_mm, int(demanda))
        # Ingresos y costos operativos por reserva
        for f in fechas:
            registros_ingresos.append({
                'fecha': f,
                'email': cfg.email_placeholder,
                'id_reserva': id_counter,
                'descripcion': cfg.descripcion_ingreso,
                'monto': cfg.ticket_promedio,
            })
            registros_costos_op.append({
                'fecha': f,
                'email': cfg.email_placeholder,
                'id_reserva': id_counter,
                'descripcion': cfg.descripcion_costo_operativo,
                'monto': cfg.costo_variable_por_reserva,
            })
            id_counter += 1

        # Gastos de marketing mensuales (1 registro al último día del mes)
        y, m = map(int, yyyy_mm.split('-'))
        last_day = monthrange(y, m)[1]
        fecha_mes = datetime(y, m, last_day, 18, 0, 0)
        registros_marketing.append({
            'fecha': fecha_mes,
            'categoria': 'Costos de Marketing',
            'categoria_2': 'Simulación',
            'descripcion': cfg.descripcion_marketing,
            'monto': float(cfg.gasto_marketing_mensual),
        })
        registros_costos_fijos.append({
            'fecha': fecha_mes,
            'categoria': 'costos fijos',
            'categoria_2': 'Simulación',
            'descripcion': cfg.descripcion_costo_fijo,
            'monto': float(cfg.costo_fijo_mensual),
        })

    df_ing = pd.DataFrame(registros_ingresos)
    df_cost_op = pd.DataFrame(registros_costos_op)
    df_mark = pd.DataFrame(registros_marketing)
    df_fijos = pd.DataFrame(registros_costos_fijos)

    # Tipos y orden
    for df in (df_ing, df_cost_op, df_mark, df_fijos):
        if not df.empty:
            df['fecha'] = pd.to_datetime(df['fecha'])

    return df_ing, df_cost_op, df_mark, df_fijos


def guardar_csv_simulados(df_ing: pd.DataFrame, df_cost_op: pd.DataFrame) -> tuple[str, str]:
    out_dir = asegurar_directorio_salida()
    p_ing = os.path.join(out_dir, 'ingresos_operativos_simulacion.csv')
    p_cost = os.path.join(out_dir, 'costos_operativos_simulacion.csv')
    cols = ['fecha', 'email', 'id_reserva', 'descripcion', 'monto']
    if not df_ing.empty:
        df_ing[cols].to_csv(p_ing, index=False)
    else:
        pd.DataFrame(columns=cols).to_csv(p_ing, index=False)
    if not df_cost_op.empty:
        df_cost_op[cols].to_csv(p_cost, index=False)
    else:
        pd.DataFrame(columns=cols).to_csv(p_cost, index=False)
    return p_ing, p_cost


def generar_consolidado(df_ing: pd.DataFrame, df_cost_op: pd.DataFrame, df_mark: pd.DataFrame, df_fijos: pd.DataFrame) -> str:
    # Mapear al formato de utilidad operativa (fecha,categoria,categoria_2,descripcion,monto)
    bloques = []
    if not df_ing.empty:
        b = df_ing[['fecha', 'monto']].copy()
        b['categoria'] = 'ingreso operativo'
        b['categoria_2'] = 'Reservas (sim)'
        b['descripcion'] = cfg.descripcion_ingreso
        bloques.append(b)
    if not df_cost_op.empty:
        b = df_cost_op[['fecha', 'monto']].copy()
        b['categoria'] = 'costo operativo'
        b['categoria_2'] = 'Por reserva (sim)'
        b['descripcion'] = cfg.descripcion_costo_operativo
        bloques.append(b)
    if not df_mark.empty:
        b = df_mark[['fecha', 'monto']].copy()
        b['categoria'] = 'Costos de Marketing'
        b['categoria_2'] = 'Simulación'
        b['descripcion'] = cfg.descripcion_marketing
        bloques.append(b)
    if not df_fijos.empty:
        b = df_fijos[['fecha', 'monto']].copy()
        b['categoria'] = 'costos fijos'
        b['categoria_2'] = 'Simulación'
        b['descripcion'] = cfg.descripcion_costo_fijo
        bloques.append(b)

    if not bloques:
        df = pd.DataFrame(columns=['fecha', 'categoria', 'categoria_2', 'descripcion', 'monto'])
    else:
        df = pd.concat(bloques, ignore_index=True)
        df = df[['fecha', 'categoria', 'categoria_2', 'descripcion', 'monto']]
        df = df.sort_values('fecha')

    out_path = os.path.join('archivos_output', 'Utilidad operativa simulacion.csv')
    df.to_csv(out_path, index=False)
    return out_path


def imprimir_resumen(df_ing: pd.DataFrame, df_cost_op: pd.DataFrame, df_mark: pd.DataFrame, df_fijos: pd.DataFrame):
    t_ing = df_ing['monto'].sum() if not df_ing.empty else 0.0
    t_cost = df_cost_op['monto'].sum() if not df_cost_op.empty else 0.0
    t_mark = df_mark['monto'].sum() if not df_mark.empty else 0.0
    t_fijos = df_fijos['monto'].sum() if not df_fijos.empty else 0.0
    utilidad = t_ing - (t_cost + t_mark + t_fijos)
    print("\n📈 RESUMEN SIMULACIÓN")
    print("=" * 40)
    print(f"Ingresos operativos: ${t_ing:,.0f}")
    print(f"Costos operativos:   ${t_cost:,.0f}")
    print(f"Marketing (mensual): ${t_mark:,.0f}")
    print(f"Costos fijos:        ${t_fijos:,.0f}")
    print("-" * 40)
    print(f"Utilidad simulada:   ${utilidad:,.0f}")


def main() -> bool:
    if not isinstance(cfg.demanda_por_mes, dict) or len(cfg.demanda_por_mes) == 0:
        print("⚠️ demanda_por_mes está vacío en inputs_simulacion.py. Agrega al menos un mes.")
    out_dir = asegurar_directorio_salida()
    print(f"📁 Directorio de salida: {out_dir}")

    df_ing, df_cost_op, df_mark, df_fijos = construir_ingresos_y_costos_simulados()

    p_ing, p_cost = guardar_csv_simulados(df_ing, df_cost_op)
    p_uo = generar_consolidado(df_ing, df_cost_op, df_mark, df_fijos)

    imprimir_resumen(df_ing, df_cost_op, df_mark, df_fijos)

    print("\n✅ Archivos generados:")
    print(f" - {p_ing}")
    print(f" - {p_cost}")
    print(f" - {p_uo}")
    return True


if __name__ == '__main__':
    main()


