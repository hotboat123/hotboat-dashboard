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
from datetime import datetime, timedelta
from calendar import monthrange
import pandas as pd
import random

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


def _dias_semana_y_finde(year: int, month: int) -> tuple[list, list]:
    """Devuelve listas de fechas datetime.date separadas en días de semana (0-4) y fin de semana (5-6)."""
    last_day = monthrange(year, month)[1]
    dias_semana = []
    dias_finde = []
    for day in range(1, last_day + 1):
        d = datetime(year, month, day).date()
        if d.weekday() < 5:
            dias_semana.append(d)
        else:
            dias_finde.append(d)
    return dias_semana, dias_finde


def _calcular_asignacion_semana_finde(yyyy_mm: str, cantidad_total: int) -> tuple[int, int]:
    """Calcula cuántas reservas van a semana y cuántas a fin de semana según el ratio mensual.
    - Usa cfg.ratio_semana_finde_por_mes.get(yyyy_mm) o cfg.ratio_semana_finde_default si no está.
    - Asigna proporcionalmente: semana = round(cantidad_total * ratio_semana/(s+f))
      y finde = cantidad_total - semana (para conservar el total).
    """
    try:
        ratio = getattr(cfg, 'ratio_semana_finde_por_mes', {}) or {}
        default_ratio = tuple(getattr(cfg, 'ratio_semana_finde_default', (3, 4)))
        r = ratio.get(yyyy_mm, default_ratio)
        semana_r, finde_r = int(r[0]), int(r[1])
        base = max(semana_r + finde_r, 1)
        semana = round(cantidad_total * (semana_r / base))
        finde = cantidad_total - semana
        return max(0, semana), max(0, finde)
    except Exception:
        # Fallback: mitad y mitad
        s = cantidad_total // 2
        return s, cantidad_total - s


def _asignar_aleatorio_en_dias(dias: list, cantidad: int, year: int, month: int, hora: int = 12) -> list:
    """Asigna `cantidad` reservas en días de la lista `dias` al azar, permitiendo múltiples en el mismo día.
    La hora se fija a `hora:00`. Si hay múltiples en el mismo día, se desempatan con minutos 0,10,20,...
    """
    if cantidad <= 0 or len(dias) == 0:
        return []
    # Semilla opcional para reproducibilidad
    try:
        seed = getattr(cfg, 'random_seed', None)
        if seed is not None:
            random.seed(seed)
    except Exception:
        pass
    escogidos = [random.choice(dias) for _ in range(cantidad)]
    # Construir datetimes y desempatarlos por bloques de 10 minutos
    asignadas = []
    contador_por_dia = {}
    for d in escogidos:
        count = contador_por_dia.get(d, 0)
        minute = (count * 10) % 60
        asignadas.append(datetime(d.year, d.month, d.day, hora, minute, 0))
        contador_por_dia[d] = count + 1
    return asignadas


def generar_fechas_para_mes(yyyy_mm: str, cantidad: int) -> list:
    """Distribuye `cantidad` reservas dentro del mes (YYYY-MM) respetando ratio semana/fin de semana.
    1) Determina cuántas van a semana y cuántas a fin de semana según cfg.ratio_semana_finde_*
    2) Asigna aleatoriamente cada grupo a sus días correspondientes.
    """
    year, month = map(int, yyyy_mm.split('-'))
    if cantidad <= 0:
        return []
    dias_semana, dias_finde = _dias_semana_y_finde(year, month)
    cant_semana, cant_finde = _calcular_asignacion_semana_finde(yyyy_mm, int(cantidad))
    fechas_semana = _asignar_aleatorio_en_dias(dias_semana, cant_semana, year, month, hora=12)
    fechas_finde = _asignar_aleatorio_en_dias(dias_finde, cant_finde, year, month, hora=12)
    fechas = sorted(fechas_semana + fechas_finde)
    return fechas


def construir_ingresos_y_costos_simulados() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    registros_ingresos = []
    registros_costos_op = []
    registros_marketing = []
    registros_costos_fijos = []

    id_counter = cfg.id_reserva_base

    for yyyy_mm, demanda in (cfg.demanda_por_mes or {}).items():
        fechas = generar_fechas_para_mes(yyyy_mm, int(demanda))
        # Resumen por mes: semana vs fin de semana
        try:
            semana_count = sum(1 for f in fechas if f.weekday() < 5)
            finde_count = len(fechas) - semana_count
            print(f"🗓️ {yyyy_mm}: {len(fechas)} reservas → semana: {semana_count}, finde: {finde_count}")
        except Exception:
            pass
        # Ingresos y costos operativos por reserva
        for f in fechas:
            registros_ingresos.append({
                'fecha': f,
                'email': cfg.email_placeholder,
                'id_reserva': id_counter,
                'descripcion': cfg.descripcion_ingreso,
                'monto': cfg.ticket_promedio,
            })
            # Costos por reserva: desglose si está habilitado, si no costo único
            try:
                usar_detalle = bool(getattr(cfg, 'usar_desglose_costos_operativos', False))
                detalle: dict = getattr(cfg, 'costo_operativo_detalle_por_reserva', {}) or {}
            except Exception:
                usar_detalle = False
                detalle = {}

            if usar_detalle and isinstance(detalle, dict) and len(detalle) > 0:
                for nombre, monto in detalle.items():
                    registros_costos_op.append({
                        'fecha': f,
                        'email': cfg.email_placeholder,
                        'id_reserva': id_counter,
                        'descripcion': str(nombre),
                        'monto': float(monto),
                    })
            else:
                registros_costos_op.append({
                    'fecha': f,
                    'email': cfg.email_placeholder,
                    'id_reserva': id_counter,
                    'descripcion': cfg.descripcion_costo_operativo,
                    'monto': cfg.costo_variable_por_reserva,
                })
            id_counter += 1

        # Pago ayudante escalonado por día (una fila por día)
        try:
            usar_escalonado = bool(getattr(cfg, 'usar_pago_ayudante_escalonado', False))
            escalas = list(getattr(cfg, 'pago_ayudante_escalas', []) or [])
            escalas_sorted = sorted(escalas, key=lambda x: x[0])
        except Exception:
            usar_escalonado = False
            escalas_sorted = []

        if usar_escalonado and len(fechas) > 0:
            # Agrupar fechas por día (YYYY-MM-DD) y contar reservas por día
            conteo_por_dia = {}
            for f in fechas:
                clave = f.date()
                conteo_por_dia[clave] = conteo_por_dia.get(clave, 0) + 1

            for dia, cantidad in conteo_por_dia.items():
                # determinar pago según la escala
                pago = 0
                for umbral, monto in escalas_sorted:
                    if cantidad >= umbral:
                        pago = monto
                    else:
                        break
                if pago == 0 and escalas_sorted:
                    pago = escalas_sorted[0][1]

                registros_costos_op.append({
                    'fecha': datetime(dia.year, dia.month, dia.day, 20, 0, 0),
                    'email': cfg.email_placeholder,
                    'id_reserva': None,
                    'descripcion': 'pago extra ayudante (diario)',
                    'monto': float(pago),
                })

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
        # Subcategoría = componente del costo (leña, agua, etc.)
        b['categoria_2'] = df_cost_op['descripcion'].values
        # Descripción: preservamos el nombre del componente
        b['descripcion'] = df_cost_op['descripcion'].values
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


