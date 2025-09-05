import sys
from pathlib import Path
import pandas as pd
import datetime
import argparse
from inputs_simulacion import pais_festivos, feriados_chile, feriados_argentina


NOMBRES_DOW = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']


def contar_por_dia(series_dt: pd.Series) -> list[int]:
    s = pd.to_datetime(series_dt, errors='coerce').dropna()
    if s.empty:
        return [0] * 7
    counts = [0] * 7
    for wd, c in s.dt.dayofweek.value_counts().sort_index().items():
        if 0 <= wd <= 6:
            counts[int(wd)] = int(c)
    return counts


def formato_resultado(counts: list[int]) -> str:
    total = sum(counts)
    if total == 0:
        return "(sin datos)"
    porc = [f"{(c/total)*100:.1f}%" for c in counts]
    pares = [f"{n}:{c} ({p})" for n, c, p in zip(NOMBRES_DOW, counts, porc)]
    return " | ".join(pares) + f"  => Total: {total}"


def build_feriados_set() -> set:
    pais = (pais_festivos or 'Chile').lower()
    fechas = feriados_chile if pais.startswith('chil') else feriados_argentina
    out = set()
    for s in fechas:
        try:
            out.add(str(pd.to_datetime(s).date()))
        except Exception:
            continue
    return out


def contar_festivo_no_festivo(series_dt: pd.Series) -> tuple[int, int]:
    feriados = build_feriados_set()
    s = pd.to_datetime(series_dt, errors='coerce').dropna()
    fest, nofest = 0, 0
    for d in s.dt.date:
        if str(d) in feriados:
            fest += 1
        else:
            nofest += 1
    return fest, nofest


def formato_festivo(fest: int, nofest: int) -> str:
    total = fest + nofest
    if total == 0:
        return "(sin datos)"
    return f"Festivo: {fest} ({fest/total:.1%}) | No festivo: {nofest} ({nofest/total:.1%})  => Total: {total}"


def stats_promedio_por_tipo_dia(series_dt: pd.Series, start_dt: pd.Timestamp | None, end_dt: pd.Timestamp | None) -> tuple[int, int, int, int, float, float]:
    """Devuelve (dias_festivos, dias_no_festivos, reservas_festivo, reservas_no_festivo, avg_festivo, avg_no).

    - dias_* se cuentan sobre el rango calendario [min(fecha)..max(fecha)] (todos los días del calendario),
      clasificando por festivo según inputs.
    - reservas_* se cuentan sobre las reservas en esos días.
    - avg_* = reservas_* / dias_* (si dias_ > 0).
    """
    feriados = build_feriados_set()
    s = pd.to_datetime(series_dt, errors='coerce').dropna()
    if start_dt is not None:
        s = s[s >= start_dt]
    if end_dt is not None:
        s = s[s <= end_dt]
    if s.empty:
        return 0, 0, 0, 0, 0.0, 0.0
    dmin = (start_dt.normalize() if start_dt is not None else s.min().normalize())
    dmax = (end_dt.normalize() if end_dt is not None else s.max().normalize())
    calendario = pd.date_range(dmin, dmax, freq='D')
    # Contar días festivos en el calendario
    dias_festivos = sum(1 for d in calendario if str(d.date()) in feriados)
    dias_no_festivos = len(calendario) - dias_festivos
    # Contar reservas por tipo
    reservas_fest, reservas_no = 0, 0
    for d in s.dt.date:
        if str(d) in feriados:
            reservas_fest += 1
        else:
            reservas_no += 1
    avg_fest = (reservas_fest / dias_festivos) if dias_festivos > 0 else 0.0
    avg_no = (reservas_no / dias_no_festivos) if dias_no_festivos > 0 else 0.0
    return dias_festivos, dias_no_festivos, reservas_fest, reservas_no, avg_fest, avg_no


def listar_festivos_en_periodo(series_dt: pd.Series, start_dt: pd.Timestamp | None, end_dt: pd.Timestamp | None) -> list[str]:
    """Lista todos los días festivos dentro del rango calendario de la serie (min..max)."""
    feriados = build_feriados_set()
    s = pd.to_datetime(series_dt, errors='coerce').dropna()
    if start_dt is not None:
        s = s[s >= start_dt]
    if end_dt is not None:
        s = s[s <= end_dt]
    if s.empty:
        return []
    dmin = (start_dt.normalize() if start_dt is not None else s.min().normalize())
    dmax = (end_dt.normalize() if end_dt is not None else s.max().normalize())
    calendario = pd.date_range(dmin, dmax, freq='D')
    dias = [str(d.date()) for d in calendario if str(d.date()) in feriados]
    return dias


def listar_festivos_con_reservas(series_dt: pd.Series, start_dt: pd.Timestamp | None, end_dt: pd.Timestamp | None) -> list[str]:
    """Lista los días festivos que tienen al menos una reserva en la serie."""
    feriados = build_feriados_set()
    s = pd.to_datetime(series_dt, errors='coerce').dropna()
    if start_dt is not None:
        s = s[s >= start_dt]
    if end_dt is not None:
        s = s[s <= end_dt]
    fechas = sorted({str(d) for d in s.dt.date if str(d) in feriados})
    return fechas


def main() -> int:
    parser = argparse.ArgumentParser(description="Ratios por día y festivo vs no festivo")
    parser.add_argument("--start", type=str, default=None, help="Fecha inicial YYYY-MM-DD (inclusive)")
    parser.add_argument("--end", type=str, default=None, help="Fecha final YYYY-MM-DD (inclusive)")
    args = parser.parse_args()

    start_dt = pd.to_datetime(args.start).tz_localize(None) if args.start else None
    end_dt = pd.to_datetime(args.end).tz_localize(None) if args.end else None
    base = Path('.')

    # Historica
    hist_path = base / 'archivos_output' / 'reservas_HotBoat.csv'
    if not hist_path.exists():
        print(f"❌ No existe {hist_path}", file=sys.stderr)
        return 1
    df_hist = pd.read_csv(hist_path)
    if 'fecha_hora_trip' not in df_hist.columns:
        print("❌ faltan columnas en reservas_HotBoat.csv", file=sys.stderr)
        return 1
    if 'Service' in df_hist.columns:
        df_hist = df_hist[df_hist['Service'] != 'Extras']
    s_hist = pd.to_datetime(df_hist['fecha_hora_trip'], errors='coerce')
    if start_dt is not None:
        s_hist = s_hist[s_hist >= start_dt]
    if end_dt is not None:
        s_hist = s_hist[s_hist <= end_dt]
    counts_hist = contar_por_dia(s_hist)

    # Simulación
    sim_path = base / 'archivos_output' / 'ingresos_operativos_simulacion.csv'
    if not sim_path.exists():
        print(f"❌ No existe {sim_path}. Ejecuta primero: python utilidad_operativa_simulacion.py", file=sys.stderr)
        return 1
    df_sim = pd.read_csv(sim_path)
    if 'fecha' not in df_sim.columns:
        print("❌ faltan columnas en ingresos_operativos_simulacion.csv", file=sys.stderr)
        return 1
    s_sim = pd.to_datetime(df_sim['fecha'], errors='coerce')
    if start_dt is not None:
        s_sim = s_sim[s_sim >= start_dt]
    if end_dt is not None:
        s_sim = s_sim[s_sim <= end_dt]
    counts_sim = contar_por_dia(s_sim)

    print("=== Distribución por día de la semana (Lun..Dom) ===")
    print("HISTÓRICA (por fecha del TRIP):")
    print(formato_resultado(counts_hist))
    print("")
    print("SIMULACIÓN (por fecha de ingreso simulado):")
    print(formato_resultado(counts_sim))
    print("")
    # Festivo vs no festivo
    fest_h, nofest_h = contar_festivo_no_festivo(s_hist)
    fest_s, nofest_s = contar_festivo_no_festivo(s_sim)
    print("=== Festivo vs No Festivo ===")
    print("HISTÓRICA:")
    print(formato_festivo(fest_h, nofest_h))
    print("")
    print("SIMULACIÓN:")
    print(formato_festivo(fest_s, nofest_s))

    # Promedios por tipo de día sobre el calendario observado
    print("")
    print("=== Promedio por tipo de día (sobre días calendario del período) ===")
    dfh = stats_promedio_por_tipo_dia(s_hist, start_dt, end_dt)
    dfs = stats_promedio_por_tipo_dia(s_sim, start_dt, end_dt)
    dias_f_h, dias_n_h, res_f_h, res_n_h, avg_f_h, avg_n_h = dfh
    dias_f_s, dias_n_s, res_f_s, res_n_s, avg_f_s, avg_n_s = dfs
    print(f"HISTÓRICA → festivos: {dias_f_h} días, demanda: {res_f_h}, promedio: {avg_f_h:.2f} | no festivos: {dias_n_h} días, demanda: {res_n_h}, promedio: {avg_n_h:.2f}")
    print(f"SIMULACIÓN → festivos: {dias_f_s} días, demanda: {res_f_s}, promedio: {avg_f_s:.2f} | no festivos: {dias_n_s} días, demanda: {res_n_s}, promedio: {avg_n_s:.2f}")

    # Listados de días festivos (histórico)
    festivos_periodo_hist = listar_festivos_en_periodo(s_hist, start_dt, end_dt)
    festivos_con_res_hist = listar_festivos_con_reservas(s_hist, start_dt, end_dt)
    print("")
    print("=== Días festivos (HISTÓRICA) ===")
    print(f"En el período (calendario): {len(festivos_periodo_hist)} → {festivos_periodo_hist}")
    print(f"Con reservas: {len(festivos_con_res_hist)} → {festivos_con_res_hist}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())


