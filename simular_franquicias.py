#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simulación de franquicias HotBoat para estimar royalties y utilidad de franquiciados.

Usa:
- inputs_simulacion.py para demanda base, ticket_promedio, costos variables, estacionalidad base
- inputs_franquicias.py para configuración de franquicias, royalty_rate y objetivo
- utilidad_operativa_simulacion.py para utilidades: reusa la expansión de demanda y helpers

Salida:
- Imprime resumen por franquicia (ventas, costo, utilidad, royalty)
- Estima cuántas franquicias modelo se requieren para superar el objetivo de royalties
"""

import sys
import math
import time
import random
import pandas as pd

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

import inputs_simulacion as cfg
import inputs_franquicias as fcfg
import utilidad_operativa_simulacion as sim


def _is_verano(month: int) -> bool:
    meses_verano = list(getattr(fcfg, 'meses_verano', getattr(cfg, 'meses_verano', [12, 1, 2])) or [12, 1, 2])
    return month in meses_verano


def _is_invierno(month: int) -> bool:
    meses_invierno = list(getattr(fcfg, 'meses_invierno', getattr(cfg, 'meses_invierno', [6, 7, 8])) or [6, 7, 8])
    return month in meses_invierno


def _ajustar_demanda_por_franquicia(demanda_map: dict, franquicia: dict) -> dict:
    """
    Ajusta la demanda base por mes según:
    - fecha de apertura (YYYY-MM)
    - estacionalidad específica de la franquicia (Verano/Invierno/normal)
    """
    salida = {}
    apertura = str(franquicia.get('apertura', '1900-01'))
    estac = franquicia.get('estacionalidad', {}) or {}
    factor_verano = float(estac.get('Verano', 1.0))
    factor_invierno = float(estac.get('Invierno', 1.0))
    factor_normal = float(estac.get('normal', 1.0))

    for ym in sorted(demanda_map.keys()):
        if ym < apertura:
            continue  # aún no abre
        base = int(demanda_map[ym])
        y, m = map(int, ym.split('-'))
        if _is_verano(m):
            factor = factor_verano
        elif _is_invierno(m):
            factor = factor_invierno
        else:
            factor = factor_normal
        val = int(round(base * factor))
        salida[ym] = max(0, val)
    return salida


def _calcular_finanzas_franquicia(demanda_mes: dict, franquicia: dict) -> dict:
    """
    Calcula ingresos, costos y utilidad mensual para la franquicia.
    Royalties = fcfg.royalty_rate * ventas.
    Costos franquiciado = arriendo + (costo_variable_por_reserva * demanda)
    """
    ticket = float(getattr(cfg, 'ticket_promedio', 0))
    cvar = fcfg.costo_variable_por_reserva_franquicia
    if cvar is None:
        cvar = float(getattr(cfg, 'costo_variable_por_reserva', 0))
    cvar = float(cvar)
    arriendo = float(franquicia.get('arriendo_mensual', 0))
    rate = float(getattr(fcfg, 'royalty_rate', 0.09))

    rows = []
    for ym in sorted(demanda_mes.keys()):
        d = int(demanda_mes[ym])
        ventas = d * ticket
        costo = arriendo + d * cvar
        utilidad = ventas - costo
        royalty = ventas * rate
        rows.append({'mes': ym, 'demanda': d, 'ventas': ventas, 'costo': costo, 'utilidad': utilidad, 'royalty': royalty})
    df = pd.DataFrame(rows)
    if not df.empty:
        df['anio'] = df['mes'].str.slice(0, 4).astype(int)
    totales = {
        'demanda_total': int(df['demanda'].sum()) if not df.empty else 0,
        'ventas_total': float(df['ventas'].sum()) if not df.empty else 0.0,
        'costo_total': float(df['costo'].sum()) if not df.empty else 0.0,
        'utilidad_total': float(df['utilidad'].sum()) if not df.empty else 0.0,
        'royalty_total': float(df['royalty'].sum()) if not df.empty else 0.0,
        'detalle': df,
    }
    return totales


def _clonar_hasta_objetivo(base_franquicia: dict, demanda_base: dict, objetivo: float, anio_objetivo: int | None) -> int:
    """Clona la franquicia de referencia hasta que la suma de royalties supere el objetivo.
    Verifica que la utilidad del franquiciado (de la franquicia modelo) sea positiva total.
    """
    demanda_f = _ajustar_demanda_por_franquicia(demanda_base, base_franquicia)
    finanzas = _calcular_finanzas_franquicia(demanda_f, base_franquicia)
    df = finanzas['detalle']
    if df is None or df.empty:
        print("⚠️ Sin datos de la franquicia modelo.")
        return 0
    # Filtrar por año objetivo (solo ese año)
    if anio_objetivo is None:
        anios = sorted(df['anio'].unique())
        anio_objetivo = anios[-1]
    df_y = df[df['anio'] == int(anio_objetivo)]
    if df_y.empty:
        print(f"⚠️ La franquicia modelo no tiene datos en el año {anio_objetivo}.")
        return 0
    utilidad_y = float(df_y['utilidad'].sum())
    royalty_y = float(df_y['royalty'].sum())
    if utilidad_y <= 0:
        print("⚠️ La franquicia modelo no es rentable para el franquiciado (utilidad <= 0). Ajusta parámetros.")
        return 0
    if royalty_y <= 0:
        print("⚠️ La franquicia modelo no genera royalties. Ajusta parámetros.")
        return 0
    # Número requerido = ceil(objetivo / royalty_modelo_en_anio)
    n = int(math.ceil(float(objetivo) / float(royalty_y)))
    return max(0, n)


def main() -> bool:
    print("🏝️ Simulación de franquicias HotBoat")
    iteraciones = int(getattr(fcfg, 'simulaciones_num_iter', 1))
    anio_objetivo_cfg = getattr(fcfg, 'objetivo_anio', None)

    # Acumuladores Monte Carlo
    royalties_por_iter = []
    n_req_por_iter = []
    util_ok_por_iter = []
    royalties_schedule_por_iter = []
    # Acumulador anual (por año) para ingreso marca (schedule) en cada iteración
    # dict[anio] -> list[royalty_en_esa_iteración]
    schedule_anual_series: dict[int, list[float]] = {}
    # Métricas fábrica
    # Utilidad por franquicia (por año objetivo) en cada iteración
    util_por_franquicia_series: dict[str, list[float]] = {}
    fabrica_ingreso_anual_series: dict[int, list[float]] = {}
    fabrica_utilidad_anual_series: dict[int, list[float]] = {}
    fabrica_costo_var_anual_series: dict[int, list[float]] = {}
    fabrica_costo_fijos_anual_series: dict[int, list[float]] = {}
    fabrica_producido_anual_series: dict[int, list[int]] = {}
    fabrica_vendido_anual_series: dict[int, list[int]] = {}
    fabrica_stock_final_anual_series: dict[int, list[int]] = {}
    fabrica_vendido_fran_anual_series: dict[int, list[int]] = {}
    fabrica_vendido_part_anual_series: dict[int, list[int]] = {}
    fabrica_ingreso_fran_anual_series: dict[int, list[float]] = {}
    fabrica_ingreso_part_anual_series: dict[int, list[float]] = {}

    for k in range(max(1, iteraciones)):
        # Control de semilla por iteración: usar base de cfg.random_seed si existe, si no tiempo
        try:
            base_seed = getattr(cfg, 'random_seed', None)
        except Exception:
            base_seed = None
        if base_seed is None:
            iter_seed = int(time.time() * 1_000_000) + k
        else:
            iter_seed = int(base_seed) + k
        # Sembrar el RNG global y desactivar reseeding interno para esta iteración
        random.seed(iter_seed)
        try:
            cfg.random_seed = None
        except Exception:
            pass
        # Demanda base (con expansión y aleatoriedad si está activa)
        demanda_map = sim.generar_demanda_expandida()
        demanda_map = sim.aplicar_aleatoriedad_demanda(demanda_map)

        total_royalties = 0.0
        anio_objetivo = anio_objetivo_cfg
        util_negativa = False

        # Desglose por franquicia (diccionario 'franquicias')
        if k == 0:
            print("\n— DESGLOSE POR FRANQUICIA (diccionario 'franquicias') —")
        for nombre, franquicia in (fcfg.franquicias or {}).items():
            dem = _ajustar_demanda_por_franquicia(demanda_map, franquicia)
            fin = _calcular_finanzas_franquicia(dem, franquicia)
            df = fin['detalle']
            if not df.empty:
                df['anio'] = df['anio'] if 'anio' in df.columns else df['mes'].str.slice(0, 4).astype(int)
                if anio_objetivo is None:
                    anios = sorted(df['anio'].unique())
                    anio_objetivo = anios[-1]
                fin_anio = df[df['anio'] == int(anio_objetivo)]['royalty'].sum()
                total_royalties += float(fin_anio)
                util_fran = float(df[df['anio'] == int(anio_objetivo)]['utilidad'].sum())
                util_por_franquicia_series.setdefault(nombre, []).append(util_fran)
            if fin['utilidad_total'] <= 0:
                util_negativa = True

        royalties_por_iter.append(total_royalties)
        util_ok_por_iter.append(not util_negativa)

        # Estimar cantidad de franquicias modelo requeridas en este experimento
        objetivo = float(getattr(fcfg, 'objetivo_royalty_total', 500_000_000))
        nombre_modelo = str(getattr(fcfg, 'nombre_franquicia_modelo', 'Franquicia 1'))
        if nombre_modelo in fcfg.franquicias:
            n_req = _clonar_hasta_objetivo(fcfg.franquicias[nombre_modelo], demanda_map, objetivo, anio_objetivo)
        else:
            n_req = 0
        n_req_por_iter.append(n_req)

        # Simular ingresos de la marca por schedule de aperturas
        schedule = getattr(fcfg, 'ingresos_marca_schedule', {}) or {}
        apertura_mes_def = int(getattr(fcfg, 'apertura_mes_default', 1))
        roy_total_schedule = 0.0
        roy_anual_map: dict[int, float] = {}
        if schedule and nombre_modelo in fcfg.franquicias:
            base = dict(fcfg.franquicias[nombre_modelo])
            # Fábrica: parámetros
            fcfg_fact = getattr(fcfg, 'factory_config', {}) or {}
            costo_unit = float(fcfg_fact.get('costo_variable_hotboat', 0))
            precio_unit = float(fcfg_fact.get('precio_venta_hotboat', 0))
            precio_part = float(fcfg_fact.get('precio_venta_particular', precio_unit))
            fijos_otros_m = float(fcfg_fact.get('costos_fijos_mensuales_otros', 0))
            arriendo_m = float(fcfg_fact.get('arriendo_mensual', 0))
            sueldo_m_unit = float(fcfg_fact.get('sueldo_mensual_por_trabajador', 0))
            trab = int(fcfg_fact.get('trabajadores', 0))
            prod_por_trab = float(fcfg_fact.get('productividad_anual_por_trabajador', 0))
            capacidad_anual = int(trab * prod_por_trab) if trab and prod_por_trab else 0
            stock_inicial = int(fcfg_fact.get('factory_initial_stock', 0))
            produce_to_capacity = bool(fcfg_fact.get('factory_produce_to_capacity', True))
            # Demanda de HotBoats por año: franquicias (schedule) + particulares
            demanda_hotboats_por_anio: dict[int, int] = {}
            for anio, cantidad in schedule.items():
                demanda_hotboats_por_anio[int(anio)] = demanda_hotboats_por_anio.get(int(anio), 0) + int(cantidad)
            demanda_part = fcfg_fact.get('particulares_unidades_por_anio', {}) or {}
            for anio, cant_p in demanda_part.items():
                demanda_hotboats_por_anio[int(anio)] = demanda_hotboats_por_anio.get(int(anio), 0) + int(cant_p)
                for j in range(int(cantidad)):
                    fr = dict(base)
                    fr['apertura'] = f"{int(anio):04d}-{int(apertura_mes_def):02d}"
                    dem_clon = _ajustar_demanda_por_franquicia(demanda_map, fr)
                    fin_clon = _calcular_finanzas_franquicia(dem_clon, fr)
                    dfc = fin_clon['detalle']
                    if not dfc.empty:
                        dfc['anio'] = dfc['anio'] if 'anio' in dfc.columns else dfc['mes'].str.slice(0, 4).astype(int)
                        # Sumar por año (para desglose anual)
                        sums = dfc.groupby('anio', as_index=False)['royalty'].sum()
                        for _, row in sums.iterrows():
                            a = int(row['anio'])
                            roy_anual_map[a] = roy_anual_map.get(a, 0.0) + float(row['royalty'])
                        # Sumar para el año objetivo (para métrica principal)
                        if anio_objetivo is not None:
                            roy_total_schedule += float(dfc[dfc['anio'] == int(anio_objetivo)]['royalty'].sum())
        royalties_schedule_por_iter.append(roy_total_schedule)
        # Registrar serie anual de esta iteración
        for a, val in roy_anual_map.items():
            schedule_anual_series.setdefault(a, []).append(float(val))
        # Fábrica: calcular ingresos y utilidad anual por capacidad y demanda
        if schedule:
            stock = stock_inicial
            for anio, demanda_unidades in sorted(demanda_hotboats_por_anio.items()):
                # Desglose de demanda por canal
                dem_fran = int(schedule.get(int(anio), 0))
                dem_part = int(demanda_part.get(int(anio), 0))
                if produce_to_capacity:
                    produccion = int(capacidad_anual)
                else:
                    # producir al menos lo necesario para cubrir demanda y reponer stock si negativo
                    neces = max(0, int(demanda_unidades) - stock)
                    produccion = min(int(capacidad_anual), neces) if capacidad_anual else neces
                # Ventas por prioridad: franquicias primero, luego particulares
                capacidad_vender = stock + produccion
                vend_fran = min(dem_fran, capacidad_vender)
                capacidad_vender -= vend_fran
                vend_part = min(dem_part, capacidad_vender)
                vendido = vend_fran + vend_part
                ingreso = float(vend_fran) * precio_unit + float(vend_part) * precio_part
                costo_var = float(produccion) * costo_unit  # Costo variable por TODAS las unidades PRODUCIDAS
                costo_sueldos = float(trab) * sueldo_m_unit * 12.0
                costos_fijos_tot = (fijos_otros_m + arriendo_m) * 12.0 + costo_sueldos
                stock = stock + produccion - vendido
                utilidad = ingreso - (costo_var + costos_fijos_tot)
                fabrica_ingreso_anual_series.setdefault(int(anio), []).append(ingreso)
                fabrica_utilidad_anual_series.setdefault(int(anio), []).append(utilidad)
                fabrica_costo_var_anual_series.setdefault(int(anio), []).append(costo_var)
                fabrica_costo_fijos_anual_series.setdefault(int(anio), []).append(costos_fijos_tot)
                fabrica_producido_anual_series.setdefault(int(anio), []).append(int(produccion))
                fabrica_vendido_anual_series.setdefault(int(anio), []).append(int(vendido))
                fabrica_stock_final_anual_series.setdefault(int(anio), []).append(int(stock))
                fabrica_vendido_fran_anual_series.setdefault(int(anio), []).append(int(vend_fran))
                fabrica_vendido_part_anual_series.setdefault(int(anio), []).append(int(vend_part))
                fabrica_ingreso_fran_anual_series.setdefault(int(anio), []).append(float(vend_fran) * precio_unit)
                fabrica_ingreso_part_anual_series.setdefault(int(anio), []).append(float(vend_part) * precio_part)

    # Estadísticos
    import statistics as stats

    def _percentile(sorted_vals: list[float], q: float) -> float:
        if not sorted_vals:
            return 0.0
        n = len(sorted_vals)
        if n == 1:
            return float(sorted_vals[0])
        # posición 0-indexed con interpolación lineal tipo nearest-rank
        pos = (n - 1) * q
        lo = int(math.floor(pos))
        hi = int(math.ceil(pos))
        if lo == hi:
            return float(sorted_vals[lo])
        frac = pos - lo
        return float(sorted_vals[lo] * (1.0 - frac) + sorted_vals[hi] * frac)

    roy_sorted = sorted(royalties_por_iter)
    n_sorted = sorted(n_req_por_iter)
    roy_sched_sorted = sorted(royalties_schedule_por_iter)
    p10_roy = _percentile(roy_sorted, 0.10)
    p50_roy = _percentile(roy_sorted, 0.50)
    p90_roy = _percentile(roy_sorted, 0.90)
    p10_sched = _percentile(roy_sched_sorted, 0.10)
    p50_sched = _percentile(roy_sched_sorted, 0.50)
    p90_sched = _percentile(roy_sched_sorted, 0.90)
    p10_n = _percentile(n_sorted, 0.10)
    p50_n = _percentile(n_sorted, 0.50)
    p90_n = _percentile(n_sorted, 0.90)
    avg_roy = float(sum(royalties_por_iter)) / len(royalties_por_iter)
    std_roy = float(stats.pstdev(royalties_por_iter)) if len(royalties_por_iter) > 1 else 0.0
    avg_n = float(sum(n_req_por_iter)) / len(n_req_por_iter)
    std_n = float(stats.pstdev(n_req_por_iter)) if len(n_req_por_iter) > 1 else 0.0
    # Probabilidades
    objetivo = float(getattr(fcfg, 'objetivo_royalty_total', 500_000_000))
    prob_supera_obj = sum(1 for v in royalties_por_iter if v >= objetivo) / len(royalties_por_iter)
    prob_util_ok = sum(1 for b in util_ok_por_iter if b) / len(util_ok_por_iter)
    avg_sched = float(sum(royalties_schedule_por_iter)) / len(royalties_schedule_por_iter) if royalties_schedule_por_iter else 0.0
    std_sched = float(stats.pstdev(royalties_schedule_por_iter)) if len(royalties_schedule_por_iter) > 1 else 0.0

    # Comparación fábrica vs tercerizar (estimación rápida con Q anual desde schedule en año objetivo)
    comp_msg = None
    try:
        fcfg_fact = getattr(fcfg, 'factory_config', {}) or {}
        c_terc = float(fcfg_fact.get('costo_tercerizado_por_unidad', 0))
        oh_terc_m = float(fcfg_fact.get('overhead_mensual_tercerizar', 0))
        # Tomar Q objetivo: suma esperada de aperturas en año_objetivo
        sched = getattr(fcfg, 'ingresos_marca_schedule', {}) or {}
        q_obj = float(sched.get(int(anio_objetivo), 0))
        # Costeo anual: fábrica (aprox) vs tercerizar
        trab = int(fcfg_fact.get('trabajadores', 0))
        prod_por_trab = float(fcfg_fact.get('productividad_anual_por_trabajador', 0))
        cap = trab * prod_por_trab
        fijos_otros_m = float(fcfg_fact.get('costos_fijos_mensuales_otros', 0))
        arriendo_m = float(fcfg_fact.get('arriendo_mensual', 0))
        sueldo_m_unit = float(fcfg_fact.get('sueldo_mensual_por_trabajador', 0))
        fijos_anuales = (fijos_otros_m + arriendo_m) * 12.0 + (trab * sueldo_m_unit * 12.0)
        c_var_unit = float(fcfg_fact.get('costo_variable_hotboat', 0))
        precio_unit = float(fcfg_fact.get('precio_venta_hotboat', 0))
        # Utilidades esperadas (ingresos por Q vendidas)
        util_fabrica_est = q_obj * (precio_unit - c_var_unit) - fijos_anuales
        util_terc_est = q_obj * (precio_unit - c_terc) - (oh_terc_m * 12.0)
        # Break-even Q
        q_be = (fijos_anuales - oh_terc_m * 12.0) / max(1e-9, (c_terc - c_var_unit)) if (c_terc - c_var_unit) > 0 else float('inf')
        comp_msg = (util_fabrica_est, util_terc_est, q_be, cap)
    except Exception:
        pass

    print(f"\n📊 Resultados Monte Carlo ({len(royalties_por_iter)} iteraciones) para el año {anio_objetivo}:")
    print("   Alcance: SUMA de TODAS las franquicias definidas en fcfg.franquicias")
    print(f"   Royalties (todas las franquicias) promedio: ${avg_roy:,.0f} (σ={std_roy:,.0f}) | p10=${p10_roy:,.0f}, p50=${p50_roy:,.0f}, p90=${p90_roy:,.0f}")
    print(f"   Franquicias necesarias (clonando modelo) promedio: {avg_n:.1f} (σ={std_n:.1f}) | p10={p10_n:.1f}, p50={p50_n:.1f}, p90={p90_n:.1f}")
    print(f"   Prob. de superar objetivo con TODAS las franquicias (${objetivo:,.0f}): {prob_supera_obj:.1%}")
    print(f"   Prob. de utilidad positiva (todas las franquicias): {prob_util_ok:.1%}")
    # Desglose: utilidad por franquicia
    if util_por_franquicia_series:
        print("\n   Utilidad por franquicia (promedio, σ, p10/p50/p90) en el año objetivo:")
        for nombre in sorted(util_por_franquicia_series.keys()):
            vals = util_por_franquicia_series[nombre]
            if not vals:
                continue
            v_sorted = sorted(vals)
            avg_u_f = float(sum(vals)) / len(vals)
            std_u_f = float(stats.pstdev(vals)) if len(vals) > 1 else 0.0
            p10_u = _percentile(v_sorted, 0.10)
            p50_u = _percentile(v_sorted, 0.50)
            p90_u = _percentile(v_sorted, 0.90)
            print(f"     - {nombre}: avg=${avg_u_f:,.0f} (σ={std_u_f:,.0f}) | p10=${p10_u:,.0f}, p50=${p50_u:,.0f}, p90=${p90_u:,.0f}")
    if royalties_schedule_por_iter:
        print("\n📦 Ingreso de la marca por schedule de aperturas:")
        nombre_modelo = str(getattr(fcfg, 'nombre_franquicia_modelo', 'Franquicia 1'))
        print(f"   Alcance: CLONANDO SOLO la franquicia modelo '{nombre_modelo}' según ingresos_marca_schedule")
        print(f"   Ingreso marca (schedule) en año {anio_objetivo} promedio: ${avg_sched:,.0f} (σ={std_sched:,.0f}) | p10=${p10_sched:,.0f}, p50=${p50_sched:,.0f}, p90=${p90_sched:,.0f}")
        # Desglose anual: promedio y σ por año
        if schedule_anual_series:
            print("\n   Ingreso marca anual (promedio ±σ) por año (schedule):")
            for a in sorted(schedule_anual_series.keys()):
                vals = schedule_anual_series[a]
                avg_a = float(sum(vals)) / len(vals)
                sd_a = float(stats.pstdev(vals)) if len(vals) > 1 else 0.0
                print(f"     - {a}: ${avg_a:,.0f} (σ={sd_a:,.0f})")
        # Fábrica: reporte anual
        if fabrica_ingreso_anual_series:
            print("\n🏭 Fábrica (venta de HotBoats a franquicias del schedule):")
            print("   Supuestos: capacidad_anual = trabajadores * productividad_anual_por_trabajador")
            for a in sorted(fabrica_ingreso_anual_series.keys()):
                vals_ing = fabrica_ingreso_anual_series[a]
                vals_u = fabrica_utilidad_anual_series.get(a, [])
                vals_cv = fabrica_costo_var_anual_series.get(a, [])
                vals_cf = fabrica_costo_fijos_anual_series.get(a, [])
                vals_prod = fabrica_producido_anual_series.get(a, [])
                vals_vend = fabrica_vendido_anual_series.get(a, [])
                vals_stock = fabrica_stock_final_anual_series.get(a, [])
                vals_vfr = fabrica_vendido_fran_anual_series.get(a, [])
                vals_vpt = fabrica_vendido_part_anual_series.get(a, [])
                vals_ing_fr = fabrica_ingreso_fran_anual_series.get(a, [])
                vals_ing_pt = fabrica_ingreso_part_anual_series.get(a, [])
                avg_ing = float(sum(vals_ing)) / len(vals_ing)
                sd_ing = float(stats.pstdev(vals_ing)) if len(vals_ing) > 1 else 0.0
                avg_u = float(sum(vals_u)) / len(vals_u) if vals_u else 0.0
                sd_u = float(stats.pstdev(vals_u)) if len(vals_u) > 1 else 0.0
                avg_cv = float(sum(vals_cv)) / len(vals_cv) if vals_cv else 0.0
                avg_cf = float(sum(vals_cf)) / len(vals_cf) if vals_cf else 0.0
                avg_prod = float(sum(vals_prod)) / len(vals_prod) if vals_prod else 0.0
                avg_vend = float(sum(vals_vend)) / len(vals_vend) if vals_vend else 0.0
                avg_stock = float(sum(vals_stock)) / len(vals_stock) if vals_stock else 0.0
                avg_vfr = float(sum(vals_vfr)) / len(vals_vfr) if vals_vfr else 0.0
                avg_vpt = float(sum(vals_vpt)) / len(vals_vpt) if vals_vpt else 0.0
                avg_ing_fr = float(sum(vals_ing_fr)) / len(vals_ing_fr) if vals_ing_fr else 0.0
                avg_ing_pt = float(sum(vals_ing_pt)) / len(vals_ing_pt) if vals_ing_pt else 0.0
                print(f"     - {a}: Ingreso=${avg_ing:,.0f} (σ={sd_ing:,.0f}) | Costos: Var=${avg_cv:,.0f}, Fijos=${avg_cf:,.0f} | Utilidad=${avg_u:,.0f} (σ={sd_u:,.0f})")
                print(f"           Producidos≈{avg_prod:.1f} | Vendidos≈{avg_vend:.1f} (Franquicias≈{avg_vfr:.1f}, Particulares≈{avg_vpt:.1f}) | Stock final≈{avg_stock:.1f}")
                print(f"           Ingreso por canal: Franquicias=${avg_ing_fr:,.0f} | Particulares=${avg_ing_pt:,.0f}")
        if comp_msg is not None:
            util_fabrica_est, util_terc_est, q_be, cap = comp_msg
            print("\n🔀 Comparación fábrica vs tercerizar (estimación rápida para año objetivo):")
            print(f"   Q esperado={int(fcfg.ingresos_marca_schedule.get(int(anio_objetivo), 0))} | Capacidad={cap:.0f} | Q_break-even≈{q_be:.1f}")
            print(f"   Utilidad estimada fábrica: ${util_fabrica_est:,.0f} vs tercerizar: ${util_terc_est:,.0f}")
    return True


if __name__ == '__main__':
    try:
        ok = main()
        sys.exit(0 if ok else 1)
    except KeyboardInterrupt:
        print("\n🛑 Proceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        sys.exit(1)


