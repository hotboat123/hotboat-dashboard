#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simulador de escenarios (pesimista, normal, optimista) para utilidad operativa

- Varia la demanda por mes según factores configurables en inputs_simulacion.py
- Reutiliza la lógica de utilidad_operativa_simulacion.py (distribución semana/fin de semana,
  crecimiento anual, pagos del ayudante, etc.)
- Imprime por terminal el ingreso mensual del ayudante (suma de pagos diarios)

Uso:
    python simular_escenarios_utilidad.py
"""

import sys
import os
from typing import Dict, Tuple
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

try:
    import utilidad_operativa_simulacion as sim
except Exception as e:
    print(f"❌ No se pudo importar utilidad_operativa_simulacion.py: {e}")
    raise


def escalar_demanda(demanda_base: Dict[str, object], factor: float) -> Dict[str, object]:
    """Escala la demanda por `factor`.
    - Si el valor es entero, escala a entero redondeado.
    - Si el valor es lista/tupla (semanal), escala cada elemento y redondea.
    """
    escalada: Dict[str, object] = {}
    f = float(factor)
    for k, v in (demanda_base or {}).items():
        if isinstance(v, (list, tuple)):
            nueva = []
            for x in list(v):
                try:
                    val = int(round(float(x) * f))
                except Exception:
                    val = 0
                if val < 0:
                    val = 0
                nueva.append(val)
            escalada[k] = nueva
        else:
            try:
                val = int(round(float(v) * f))
            except Exception:
                val = 0
            if val < 0:
                val = 0
            escalada[k] = val
    return escalada


def resumen_ingreso_ayudante_por_mes(df_cost_op: pd.DataFrame) -> pd.DataFrame:
    """Filtra pagos del ayudante y resume por mes calendario (YYYY-MM).
    Devuelve columnas: mes, total_pagado, ayudantes_totales, pago_unitario_promedio, ingreso_por_ayudante_promedio
    """
    if df_cost_op is None or df_cost_op.empty:
        return pd.DataFrame(columns=["mes", "total_pagado", "ayudantes_totales", "pago_unitario_promedio", "ingreso_por_ayudante_promedio"])
    df = df_cost_op.copy()
    df = df[(df["descripcion"].astype(str).str.lower() == "pago extra ayudante (diario)")]
    if df.empty:
        return pd.DataFrame(columns=["mes", "total_pagado", "ayudantes_totales", "pago_unitario_promedio", "ingreso_por_ayudante_promedio"])
    df["mes"] = pd.to_datetime(df["fecha"]).dt.to_period("M").astype(str)
    # Asegurar columnas nuevas existen
    if "ayudantes_pagados" not in df.columns:
        df["ayudantes_pagados"] = 1
    if "pago_unitario" not in df.columns:
        # Si no existe, derivar unitario como monto (asumiendo 1 ayudante)
        df["pago_unitario"] = df["monto"]
    # Resumen total por mes
    agg = df.groupby("mes", as_index=False).agg(
        total_pagado=("monto", "sum"),
        ayudantes_totales=("ayudantes_pagados", "sum"),
        pago_unitario_promedio=("pago_unitario", "mean"),
    )
    agg["ingreso_por_ayudante_promedio"] = agg.apply(
        lambda r: (r["total_pagado"] / r["ayudantes_totales"]) if r["ayudantes_totales"] not in (0, None) else 0.0,
        axis=1,
    )
    # Breakdown por ayudante (1..N) dentro del mes
    if "ayudante" in df.columns:
        detalle = df.groupby(["mes", "ayudante"], as_index=False)["monto"].sum().rename(columns={"monto": "ingreso_ayudante"})
        # Pivot opcional para mostrar columnas ayudante_1, ayudante_2, ...
        pivot = detalle.pivot(index="mes", columns="ayudante", values="ingreso_ayudante").fillna(0.0)
        pivot.columns = [f"ayudante_{int(c)}" for c in pivot.columns]
        agg = agg.merge(pivot.reset_index(), on="mes", how="left")
    return agg.sort_values("mes")


def resumen_utilidad_operativa_mensual(
    df_ing: pd.DataFrame,
    df_cost_op: pd.DataFrame,
    df_mark: pd.DataFrame,
    df_fijos: pd.DataFrame,
) -> pd.DataFrame:
    """Calcula utilidad operativa por mes: ingresos - (costos op + marketing + fijos)."""
    def group_month_sum(df: pd.DataFrame) -> pd.DataFrame:
        if df is None or df.empty:
            return pd.DataFrame(columns=["mes", "monto"]).assign(monto=pd.Series(dtype=float))
        d = df.copy()
        d["mes"] = pd.to_datetime(d["fecha"]).dt.to_period("M").astype(str)
        return d.groupby("mes", as_index=False)["monto"].sum()

    g_ing = group_month_sum(df_ing).rename(columns={"monto": "ingresos"})
    g_op = group_month_sum(df_cost_op).rename(columns={"monto": "costos_op"})
    g_mark = group_month_sum(df_mark).rename(columns={"monto": "marketing"})
    g_fijos = group_month_sum(df_fijos).rename(columns={"monto": "fijos"})

    # Unir por mes (outer) y rellenar NaN con 0
    res = g_ing.merge(g_op, on="mes", how="outer")
    res = res.merge(g_mark, on="mes", how="outer")
    res = res.merge(g_fijos, on="mes", how="outer")
    for c in ["ingresos", "costos_op", "marketing", "fijos"]:
        if c in res.columns:
            res[c] = res[c].fillna(0.0)
        else:
            res[c] = 0.0
    res["utilidad"] = res["ingresos"] - (res["costos_op"] + res["marketing"] + res["fijos"]) 
    res = res.sort_values("mes")
    return res


def ejecutar_escenario(nombre: str, factor: float) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Ejecuta el escenario escalando la demanda y construyendo los DataFrames de simulación."""
    print("\n" + "-" * 60)
    print(f"🎯 Escenario: {nombre} (factor demanda = {factor})")
    print("-" * 60)

    # Guardar demanda original
    demanda_original = dict(getattr(cfg, 'demanda_por_mes', {}) or {})

    # Aplicar escala al mapa base; el resto (crecimiento/expansión) lo hace sim.generar_demanda_expandida()
    demanda_escalada = escalar_demanda(demanda_original, factor)

    # Monkey-patch: reemplazar temporalmente la demanda base
    cfg.demanda_por_mes = demanda_escalada

    try:
        df_ing, df_cost_op, df_mark, df_fijos = sim.construir_ingresos_y_costos_simulados()
        # Mostrar resumen mensual de ayudante
        resumen = resumen_ingreso_ayudante_por_mes(df_cost_op)
        # Contar reservas por mes
        reservas_por_mes = {}
        try:
            if df_ing is not None and not df_ing.empty:
                dcnt = df_ing.copy()
                dcnt["mes"] = pd.to_datetime(dcnt["fecha"]).dt.to_period("M").astype(str)
                gcnt = dcnt.groupby("mes", as_index=False)["fecha"].count().rename(columns={"fecha": "reservas_mes"})
                reservas_por_mes = {r["mes"]: int(r["reservas_mes"]) for _, r in gcnt.iterrows()}
        except Exception:
            reservas_por_mes = {}
        if resumen.empty:
            print("ℹ️  No hay pagos al ayudante en este escenario")
        else:
            print("👷 Pagos a ayudantes por mes:")
            for _, row in resumen.iterrows():
                total = row.get('total_pagado', 0.0)
                ayud_tot = int(row.get('ayudantes_totales', 0) or 0)
                unit_prom = row.get('pago_unitario_promedio', 0.0)
                por_ayud = row.get('ingreso_por_ayudante_promedio', 0.0)
                reservas_mes = reservas_por_mes.get(row['mes'], 0)
                print(f"  - {row['mes']}: total ${total:,.0f} | reservas {reservas_mes} | Total servicio ayudantes {ayud_tot} | Costo total remuneracion prom. ${unit_prom:,.0f} | Ganancia promedio ayudantes: ${por_ayud:,.0f}")
                # Mostrar detalle por ayudante si existe
                cols_det = [c for c in row.index if str(c).startswith('ayudante_')]
                if cols_det:
                    detalle_txt = ", ".join([f"{c.replace('ayudante_', 'ayudante ')}: ${row[c]:,.0f}" for c in cols_det])
                    print(f"      Detalle → {detalle_txt}")

        # Utilidad total mensual y total (incluye costos fijos y marketing)
        uo = resumen_utilidad_operativa_mensual(df_ing, df_cost_op, df_mark, df_fijos)
        if uo.empty:
            print("ℹ️  No hay datos para calcular utilidad operativa")
        else:
            print("💼 Utilidad total mensual:")
            for _, row in uo.iterrows():
                print(f"  - {row['mes']}: ${row['utilidad']:,.0f}")
            total_uo = uo["utilidad"].sum()
            print(f"🧮 Utilidad total del escenario: ${total_uo:,.0f}")
        return df_ing, df_cost_op, df_mark, df_fijos
    finally:
        # Restaurar demanda original
        cfg.demanda_por_mes = demanda_original


def main() -> bool:
    # Leer escenarios desde inputs (con defaults)
    try:
        escenarios = dict(getattr(cfg, 'escenarios_demanda', {}) or {
            'pesimista': 0.5,
            'normal': 1.0,
            'optimista': 1.5,
        })
    except Exception:
        escenarios = {'pesimista': 0.5, 'normal': 1.0, 'optimista': 1.5}

    # Chequear flag para ejecutar escenarios
    try:
        ejecutar = bool(getattr(cfg, 'ejecutar_escenarios_demanda', True))
    except Exception:
        ejecutar = True
    if not ejecutar:
        factor_normal = float(escenarios.get('normal', 1.0))
        print("ℹ️ ejecutar_escenarios_demanda=False → se ejecutará solo el escenario 'normal'.")
        ejecutar_escenario('normal', factor_normal)
        print("\n✅ Escenario 'normal' completado")
        return True

    base = getattr(cfg, 'demanda_por_mes', None)
    if not isinstance(base, dict) or len(base) == 0:
        print("⚠️ demanda_por_mes está vacío en inputs_simulacion.py. Agrega al menos un mes.")

    print("🚀 Simulador de escenarios de demanda")
    print("Escenarios a ejecutar:")
    for nombre, factor in escenarios.items():
        print(f" - {nombre}: factor {factor}")

    resultados: Dict[str, Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]] = {}

    for nombre, factor in escenarios.items():
        resultados[nombre] = ejecutar_escenario(nombre, float(factor))

    print("\n✅ Simulación de escenarios completada")
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


