import math
from pathlib import Path
import sys

import pandas as pd


def compute_weekday_weekend_ratio(series: pd.Series) -> tuple[int, int, int, str]:
    """Return (total, weekdays, weekend, simplified_ratio_str) for a datetime series.

    Weekend is Saturday/Sunday (dayofweek >= 5). Weekdays is Monday-Friday.
    """
    datetimes = pd.to_datetime(series, errors="coerce")
    datetimes = datetimes.dropna()
    if datetimes.empty:
        return 0, 0, 0, "0:0"

    is_weekend = datetimes.dt.dayofweek >= 5
    weekend_count = int(is_weekend.sum())
    weekday_count = int((~is_weekend).sum())
    total = weekday_count + weekend_count

    gcd = math.gcd(weekday_count, weekend_count) if (weekday_count and weekend_count) else 1
    ratio_str = f"{weekday_count // gcd}:{weekend_count // gcd}"
    return total, weekday_count, weekend_count, ratio_str


def main() -> int:
    csv_path = Path("archivos_output") / "reservas_HotBoat.csv"
    if not csv_path.exists():
        print(f"Error: no se encontró el archivo: {csv_path}", file=sys.stderr)
        return 1

    df = pd.read_csv(csv_path)
    if "Service" in df.columns:
        df = df[df["Service"] != "Extras"].copy()

    # Validar columnas
    for col in ("fecha_hora_trip", "fecha_hora_creacion_reserva"):
        if col not in df.columns:
            print(f"Error: falta la columna '{col}' en {csv_path}", file=sys.stderr)
            return 1

    # Periodo (según fecha_hora_trip)
    trip_times = pd.to_datetime(df["fecha_hora_trip"], errors="coerce").dropna()
    periodo = "desconocido"
    if not trip_times.empty:
        periodo = f"{trip_times.min().date()} → {trip_times.max().date()}"

    t_total, t_wd, t_we, t_ratio = compute_weekday_weekend_ratio(df["fecha_hora_trip"]) 
    c_total, c_wd, c_we, c_ratio = compute_weekday_weekend_ratio(df["fecha_hora_creacion_reserva"]) 

    print("=== Ratio semana : fin de semana (desde que se comenzó) ===")
    print(f"Periodo (según trip): {periodo}")
    print("")
    if t_total > 0:
        print("Usando fecha del TRIP:")
        print(f"  Total: {t_total}")
        print(f"  Semana (Lun-Vie): {t_wd} ({t_wd / t_total:.1%})")
        print(f"  Fin de semana (Sab-Dom): {t_we} ({t_we / t_total:.1%})")
        print(f"  Ratio semana:fin_de_semana = {t_ratio}")
    else:
        print("Usando fecha del TRIP: sin datos válidos")

    print("")
    if c_total > 0:
        print("Usando fecha de CREACIÓN de la reserva:")
        print(f"  Total: {c_total}")
        print(f"  Semana (Lun-Vie): {c_wd} ({c_wd / c_total:.1%})")
        print(f"  Fin de semana (Sab-Dom): {c_we} ({c_we / c_total:.1%})")
        print(f"  Ratio semana:fin_de_semana = {c_ratio}")
    else:
        print("Usando fecha de CREACIÓN: sin datos válidos")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


