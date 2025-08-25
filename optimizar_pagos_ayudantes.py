#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Optimización de pagos de ayudantes (base + variable*alpha + piso) con escenarios

Evalúa combinaciones de parámetros y recomienda la mejor, priorizando:
1) Utilidad total (ingresos - costos op ajustados - marketing - fijos)
2) Estabilidad del ingreso de ayudantes (desviación estándar mensual por ayudante)

Configuración en inputs_simulacion.py (opcional):
optimizar_pagos_config = {
    'alphas': [0.6, 0.8, 1.0],
    'base_invierno': [150_000, 200_000, 250_000],
    'base_verano':   [250_000, 300_000, 350_000],
    'piso_invierno': [200_000, 250_000, 300_000],
    'piso_verano':   [300_000, 350_000, 400_000],
    'escenarios': ['normal'],  # o ['pesimista','normal','optimista']
}

Uso:
    python optimizar_pagos_ayudantes.py
"""

import sys
import os
from itertools import product
from typing import Dict, List, Tuple
import pandas as pd

# UTF-8
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

try:
    import utilidad_operativa_simulacion as sim
except Exception as e:
    print(f"❌ No se pudo importar utilidad_operativa_simulacion.py: {e}")
    raise


def _mes_str(dt: pd.Timestamp) -> str:
    return pd.to_datetime(dt).to_period("M").strftime("%Y-%m")


def _is_verano(month: int) -> bool:
    meses_verano = list(getattr(cfg, 'meses_verano', [12, 1, 2]) or [12, 1, 2])
    return month in meses_verano


def _is_invierno(month: int) -> bool:
    meses_invierno = list(getattr(cfg, 'meses_invierno', [6, 7, 8]) or [6, 7, 8])
    return month in meses_invierno


def _scale_demanda(demanda_base: Dict[str, int], factor: float) -> Dict[str, int]:
    esc = {}
    for k, v in (demanda_base or {}).items():
        try:
            esc[k] = int(round(float(v) * float(factor)))
        except Exception:
            esc[k] = 0
    return esc


def _group_month_sum(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=["mes", "monto"]).assign(monto=pd.Series(dtype=float))
    d = df.copy()
    d["mes"] = pd.to_datetime(d["fecha"]).dt.to_period("M").astype(str)
    return d.groupby("mes", as_index=False)["monto"].sum()


def _helper_variable_total_por_mes(df_cost_op: pd.DataFrame) -> pd.DataFrame:
    if df_cost_op is None or df_cost_op.empty:
        return pd.DataFrame(columns=["mes", "var_total"]).assign(var_total=pd.Series(dtype=float))
    d = df_cost_op[df_cost_op["descripcion"].astype(str).str.lower() == "pago extra ayudante (diario)"].copy()
    if d.empty:
        return pd.DataFrame(columns=["mes", "var_total"]).assign(var_total=pd.Series(dtype=float))
    d["mes"] = pd.to_datetime(d["fecha"]).dt.to_period("M").astype(str)
    return d.groupby("mes", as_index=False)["monto"].sum().rename(columns={"monto": "var_total"})


def _utilidad_total_ajustada_por_mes(
    df_ing: pd.DataFrame,
    df_cost_op: pd.DataFrame,
    df_mark: pd.DataFrame,
    df_fijos: pd.DataFrame,
    alpha: float,
    base_inv: float,
    base_ver: float,
    piso_inv: float,
    piso_ver: float,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Devuelve:
    - df_utilidad: mes, ingresos, costos_op_ajustados, marketing, fijos, utilidad
    - df_ayudante: mes, ingreso_total_ayudantes, ingreso_por_ayudante
    """
    num_ayudantes = int(getattr(cfg, 'numero_ayudantes', 1))

    g_ing = _group_month_sum(df_ing).rename(columns={"monto": "ingresos"})
    g_op = _group_month_sum(df_cost_op).rename(columns={"monto": "costos_op"})
    g_mark = _group_month_sum(df_mark).rename(columns={"monto": "marketing"})
    g_fijos = _group_month_sum(df_fijos).rename(columns={"monto": "fijos"})

    # Variable ayudantes original por mes y versión escalada por alpha
    helper_var = _helper_variable_total_por_mes(df_cost_op)  # ya incluye todos los ayudantes
    helper_var["var_alpha"] = helper_var["var_total"] * float(alpha)

    # Construir calendario de meses presentes
    meses = sorted(set(g_ing["mes"]).union(g_op["mes"]).union(g_mark["mes"]).union(g_fijos["mes"]))
    rows_util = []
    rows_help = []

    for mes in meses:
        y, m = map(int, mes.split('-'))
        ingresos = float(g_ing.loc[g_ing["mes"] == mes, "ingresos"].sum())
        costos_op = float(g_op.loc[g_op["mes"] == mes, "costos_op"].sum())
        marketing = float(g_mark.loc[g_mark["mes"] == mes, "marketing"].sum())
        fijos = float(g_fijos.loc[g_fijos["mes"] == mes, "fijos"].sum())

        var_total = float(helper_var.loc[helper_var["mes"] == mes, "var_total"].sum())
        var_alpha = float(helper_var.loc[helper_var["mes"] == mes, "var_alpha"].sum())

        # Ajuste de costos operativos: reemplazar variable original por escalada
        otros_costos_op = costos_op - var_total
        costos_op_aj = otros_costos_op + var_alpha

        # Base mensual (por ayudante) según estación
        if _is_verano(m):
            base_per_helper = float(base_ver)
            piso_per_helper = float(piso_ver)
        elif _is_invierno(m):
            base_per_helper = float(base_inv)
            piso_per_helper = float(piso_inv)
        else:
            # Meses "neutros": usar promedio simple de inv/ver
            base_per_helper = float(base_inv + base_ver) / 2.0
            piso_per_helper = float(piso_inv + piso_ver) / 2.0

        base_total = base_per_helper * num_ayudantes

        # Ingreso de ayudantes después de base y variable escalada
        ingreso_total_ayudantes_sin_piso = base_total + var_alpha
        ingreso_por_ayudante_sin_piso = ingreso_total_ayudantes_sin_piso / max(1, num_ayudantes)

        # Top-up de piso mensual (por ayudante)
        topup_per_helper = max(0.0, piso_per_helper - ingreso_por_ayudante_sin_piso)
        topup_total = topup_per_helper * num_ayudantes

        ingreso_total_ayudantes = ingreso_total_ayudantes_sin_piso + topup_total
        ingreso_por_ayudante = ingreso_total_ayudantes / max(1, num_ayudantes)

        # Costos operativos ajustados: sumar base y top-up
        costos_op_aj += base_total + topup_total

        utilidad = ingresos - (costos_op_aj + marketing + fijos)

        rows_util.append({
            "mes": mes,
            "ingresos": ingresos,
            "costos_op_ajustados": costos_op_aj,
            "marketing": marketing,
            "fijos": fijos,
            "utilidad": utilidad,
        })
        rows_help.append({
            "mes": mes,
            "ingreso_total_ayudantes": ingreso_total_ayudantes,
            "ingreso_por_ayudante": ingreso_por_ayudante,
        })

    df_util = pd.DataFrame(rows_util).sort_values("mes")
    df_help = pd.DataFrame(rows_help).sort_values("mes")
    return df_util, df_help


def _run_escenario_con_parametros(nombre: str, factor: float, alpha: float, base_inv: float, base_ver: float, piso_inv: float, piso_ver: float) -> Tuple[pd.DataFrame, pd.DataFrame]:
    demanda_original = dict(getattr(cfg, 'demanda_por_mes', {}) or {})
    try:
        cfg.demanda_por_mes = _scale_demanda(demanda_original, factor)
        df_ing, df_cost_op, df_mark, df_fijos = sim.construir_ingresos_y_costos_simulados()
        return _utilidad_total_ajustada_por_mes(df_ing, df_cost_op, df_mark, df_fijos, alpha, base_inv, base_ver, piso_inv, piso_ver)
    finally:
        cfg.demanda_por_mes = demanda_original


def _score_parametros(df_util_por_escenario: Dict[str, pd.DataFrame], df_help_por_escenario: Dict[str, pd.DataFrame]) -> Tuple[float, float, float]:
    """Devuelve (utilidad_total_sum, -std_promedio_por_ayudante, utilidad_min) para ordenar.
    Priorizamos utilidad total sumada, y menor desviación estándar (más estabilidad)."""
    utilidad_total_sum = 0.0
    stds = []
    utilidades = []
    for _, df_util in df_util_por_escenario.items():
        utilidad_total_sum += float(df_util["utilidad"].sum())
        utilidades.append(float(df_util["utilidad"].sum()))
    for _, df_help in df_help_por_escenario.items():
        if not df_help.empty:
            stds.append(float(df_help["ingreso_por_ayudante"].std(ddof=0)))
    std_prom = float(sum(stds) / len(stds)) if stds else 0.0
    utilidad_min = min(utilidades) if utilidades else 0.0
    return utilidad_total_sum, -std_prom, utilidad_min


def main() -> bool:
    escenarios = dict(getattr(cfg, 'escenarios_demanda', {'pesimista': 0.5, 'normal': 1.0, 'optimista': 1.5}))
    optim_cfg = getattr(cfg, 'optimizar_pagos_config', None) or {
        'alphas': [0.6, 0.8, 1.0],
        'base_invierno': [150_000, 200_000, 250_000],
        'base_verano':   [250_000, 300_000, 350_000],
        'piso_invierno': [200_000, 250_000, 300_000],
        'piso_verano':   [300_000, 350_000, 400_000],
        'escenarios': ['normal'],
    }

    escenarios_a_usar: List[str] = list(optim_cfg.get('escenarios') or ['normal'])
    pares_escenarios = [(n, escenarios.get(n, 1.0)) for n in escenarios_a_usar if n in escenarios]
    if not pares_escenarios:
        pares_escenarios = [('normal', 1.0)]

    alphas = list(optim_cfg.get('alphas') or [1.0])
    bases_inv = list(optim_cfg.get('base_invierno') or [200_000])
    bases_ver = list(optim_cfg.get('base_verano') or [300_000])
    pisos_inv = list(optim_cfg.get('piso_invierno') or [250_000])
    pisos_ver = list(optim_cfg.get('piso_verano') or [350_000])

    print("🧪 Ejecutando grid de parámetros...")
    print(f" - Escenarios: {[n for n,_ in pares_escenarios]}")
    print(f" - alphas: {alphas}")
    print(f" - base_invierno: {bases_inv}")
    print(f" - base_verano: {bases_ver}")
    print(f" - piso_invierno: {pisos_inv}")
    print(f" - piso_verano: {pisos_ver}")

    candidatos = []
    for alpha, base_inv, base_ver, piso_inv, piso_ver in product(alphas, bases_inv, bases_ver, pisos_inv, pisos_ver):
        df_util_por_esc = {}
        df_help_por_esc = {}
        for nombre, factor in pares_escenarios:
            df_util, df_help = _run_escenario_con_parametros(nombre, float(factor), float(alpha), float(base_inv), float(base_ver), float(piso_inv), float(piso_ver))
            df_util_por_esc[nombre] = df_util
            df_help_por_esc[nombre] = df_help
        score = _score_parametros(df_util_por_esc, df_help_por_esc)
        candidatos.append((score, (alpha, base_inv, base_ver, piso_inv, piso_ver), df_util_por_esc, df_help_por_esc))

    # Orden: mayor utilidad_total_sum, menor std promedio, mayor utilidad mínima (robustez)
    candidatos.sort(key=lambda x: (x[0][0], x[0][1], x[0][2]), reverse=True)

    if not candidatos:
        print("⚠️ No se generaron candidatos.")
        return False

    top = candidatos[0]
    (_, (alpha, base_inv, base_ver, piso_inv, piso_ver), df_util_por_esc, df_help_por_esc) = top

    print("\n🏆 Recomendación de parámetros")
    print(f" - alpha (factor variable): {alpha}")
    print(f" - base mensual por ayudante (invierno): ${base_inv:,.0f}")
    print(f" - base mensual por ayudante (verano):  ${base_ver:,.0f}")
    print(f" - piso mensual por ayudante (invierno): ${piso_inv:,.0f}")
    print(f" - piso mensual por ayudante (verano):  ${piso_ver:,.0f}")

    for nombre in df_util_por_esc:
        df_util = df_util_por_esc[nombre]
        df_help = df_help_por_esc[nombre]
        print(f"\n📈 Escenario '{nombre}':")
        print(f"   Utilidad total: ${float(df_util['utilidad'].sum()):,.0f}")
        if not df_help.empty:
            std = float(df_help['ingreso_por_ayudante'].std(ddof=0))
            print(f"   Desv. estándar ingreso por ayudante: ${std:,.0f}")
            print("   Ingreso por ayudante (mensual):")
            for _, r in df_help.iterrows():
                print(f"     - {r['mes']}: ${r['ingreso_por_ayudante']:,.0f}")

    print("\n✅ Optimización finalizada")
    return True


if __name__ == "__main__":
    try:
        ok = main()
        sys.exit(0 if ok else 1)
    except KeyboardInterrupt:
        print("\n🛑 Proceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        sys.exit(1)



