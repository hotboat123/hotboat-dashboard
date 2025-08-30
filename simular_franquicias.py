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
    p10_roy = _percentile(roy_sorted, 0.10)
    p50_roy = _percentile(roy_sorted, 0.50)
    p90_roy = _percentile(roy_sorted, 0.90)
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

    print(f"\n📊 Resultados Monte Carlo ({len(royalties_por_iter)} iteraciones) en {anio_objetivo}:")
    print(f"   Royalties totales promedio: ${avg_roy:,.0f} (σ={std_roy:,.0f}) | p10=${p10_roy:,.0f}, p50=${p50_roy:,.0f}, p90=${p90_roy:,.0f}")
    print(f"   Franquicias necesarias promedio: {avg_n:.1f} (σ={std_n:.1f}) | p10={p10_n:.1f}, p50={p50_n:.1f}, p90={p90_n:.1f}")
    print(f"   Probabilidad de superar objetivo (${objetivo:,.0f}): {prob_supera_obj:.1%}")
    print(f"   Probabilidad de utilidad positiva (todas las franquicias): {prob_util_ok:.1%}")
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


