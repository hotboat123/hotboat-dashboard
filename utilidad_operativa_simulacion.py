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
        # Si cfg.random_seed es None, asumimos que ya se sembró desde fuera (Monte Carlo)
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


def generar_demanda_expandida() -> dict:
    """Devuelve un diccionario YYYY-MM -> demanda, expandiendo a años futuros si está habilitado.
    - No sobrescribe meses existentes salvo que cfg.sobrescribir_demanda_existente_con_crecimiento sea True.
    - Para cada mes base, genera el mismo mes en años siguientes hasta `simular_hasta_anio`,
      multiplicando por (1 + tasa)^años_transcurridos y redondeando a entero.
    """
    try:
        demanda_base = dict(getattr(cfg, 'demanda_por_mes', {}) or {})
    except Exception:
        demanda_base = {}
    if not demanda_base:
        return {}

    try:
        expandir = bool(getattr(cfg, 'expandir_demanda_con_crecimiento', False))
        tasa = float(getattr(cfg, 'tasa_crecimiento_anual', 0.0) or 0.0)
        hasta_anio = int(getattr(cfg, 'simular_hasta_anio', 0) or 0)
        sobrescribir = bool(getattr(cfg, 'sobrescribir_demanda_existente_con_crecimiento', False))
    except Exception:
        expandir = False
        tasa = 0.0
        hasta_anio = 0
        sobrescribir = False

    if not expandir or tasa <= 0.0 or hasta_anio <= 0:
        return demanda_base

    added = 0
    # Iterar ordenado para determinismo
    for key in sorted(list(demanda_base.keys())):
        try:
            y, m = map(int, key.split('-'))
        except Exception:
            continue
        base_val = int(demanda_base[key])
        # Generar años siguientes
        for year in range(y + 1, hasta_anio + 1):
            new_key = f"{year:04d}-{m:02d}"
            years_elapsed = year - y
            new_val = int(round(base_val * ((1.0 + tasa) ** years_elapsed)))
            if new_val < 0:
                new_val = 0
            if new_key in demanda_base and not sobrescribir:
                continue
            demanda_base[new_key] = new_val
            added += 1

    print(f"🔁 Expansión de demanda: añadidos {added} meses hasta {hasta_anio} con tasa {tasa:.2%} anual.")
    return demanda_base


def aplicar_aleatoriedad_demanda(demanda_map: dict) -> dict:
    """
    Aplica aleatoriedad uniforme por mes: para cada mes YYYY-MM con demanda d,
    muestrea d' ~ Uniform([(1-r)*d, (1+r)*d]) y redondea a entero (>=0).
    Controlado por cfg.usar_aleatoriedad_demanda y cfg.demanda_uniforme_rango_pct.
    Reutiliza cfg.random_seed si está definido para reproducibilidad.
    """
    try:
        usar = bool(getattr(cfg, 'usar_aleatoriedad_demanda', False))
        rango = float(getattr(cfg, 'demanda_uniforme_rango_pct', 0.0) or 0.0)
    except Exception:
        usar = False
        rango = 0.0
    if not usar or rango <= 0.0:
        return demanda_map

    try:
        seed = getattr(cfg, 'random_seed', None)
        if seed is not None:
            random.seed(seed)
    except Exception:
        pass

    salida = dict(demanda_map)
    for k, v in list(salida.items()):
        try:
            base = float(v)
            low = max(0.0, (1.0 - rango) * base)
            high = (1.0 + rango) * base
            sampled = int(round(random.uniform(low, high)))
            salida[k] = sampled
        except Exception:
            continue
    return salida


def construir_ingresos_y_costos_simulados() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    registros_ingresos = []
    registros_costos_op = []
    registros_marketing = []
    registros_costos_fijos = []

    id_counter = cfg.id_reserva_base

    demanda_map = generar_demanda_expandida()
    demanda_map = aplicar_aleatoriedad_demanda(demanda_map)
    for yyyy_mm in sorted((demanda_map or {}).keys()):
        demanda = demanda_map[yyyy_mm]
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

                # Multiplicar por la cantidad de ayudantes
                try:
                    num_ayudantes = int(getattr(cfg, 'numero_ayudantes', 1))
                except Exception:
                    num_ayudantes = 1
                monto_total_ayudantes = float(pago) * max(1, num_ayudantes)

                registros_costos_op.append({
                    'fecha': datetime(dia.year, dia.month, dia.day, 20, 0, 0),
                    'email': cfg.email_placeholder,
                    'id_reserva': None,
                    'descripcion': 'pago extra ayudante (diario)',
                    'monto': monto_total_ayudantes,
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
        # Costo fijo mensual (con soporte estacional opcional)
        try:
            usar_estacional = bool(getattr(cfg, 'usar_costo_fijo_estacional', False))
            meses_verano = list(getattr(cfg, 'meses_verano', [12, 1, 2]) or [12, 1, 2])
            meses_invierno = list(getattr(cfg, 'meses_invierno', [6, 7, 8]) or [6, 7, 8])
            costo_verano = float(getattr(cfg, 'costo_fijo_mensual_verano', getattr(cfg, 'costo_fijo_mensual', 0)))
            costo_invierno = float(getattr(cfg, 'costo_fijo_mensual_invierno', getattr(cfg, 'costo_fijo_mensual', 0)))
            if usar_estacional:
                if m in meses_verano:
                    costo_fijo_mes = costo_verano
                elif m in meses_invierno:
                    costo_fijo_mes = costo_invierno
                else:
                    costo_fijo_mes = float(getattr(cfg, 'costo_fijo_mensual', 0))
            else:
                costo_fijo_mes = float(getattr(cfg, 'costo_fijo_mensual', 0))
        except Exception:
            costo_fijo_mes = float(getattr(cfg, 'costo_fijo_mensual', 0))

        registros_costos_fijos.append({
            'fecha': fecha_mes,
            'categoria': 'costos fijos',
            'categoria_2': 'Simulación',
            'descripcion': cfg.descripcion_costo_fijo,
            'monto': costo_fijo_mes,
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


