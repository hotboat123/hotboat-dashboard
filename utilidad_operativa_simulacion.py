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


def _build_feriados_set() -> set:
    """Construye el conjunto de fechas (YYYY-MM-DD) marcadas como feriado según país en cfg."""
    try:
        pais = str(getattr(cfg, 'pais_festivos', 'Chile') or 'Chile').lower()
    except Exception:
        pais = 'chile'
    fechas: list[str] = []
    try:
        if pais.startswith('chil'):
            fechas = list(getattr(cfg, 'feriados_chile', []) or [])
        elif pais.startswith('arg'):
            fechas = list(getattr(cfg, 'feriados_argentina', []) or [])
        else:
            fechas = list(getattr(cfg, 'feriados_chile', []) or [])
    except Exception:
        fechas = []
    # Normalizar formato
    out = set()
    for s in fechas:
        try:
            out.add(str(pd.to_datetime(s).date()))
        except Exception:
            continue
    return out


def _es_festivo(d: datetime.date, feriados_set: set, marcar_finde_como_festivo: bool) -> bool:
    ymd = str(d)
    if ymd in feriados_set:
        return True
    if marcar_finde_como_festivo and d.weekday() >= 5:
        # Si sábado o domingo están marcados como feriado explícitamente, ya devolvió True arriba.
        # Aquí extendemos: si hay feriado en ese fin de semana, marcar ambos días como festivos.
        # Buscar el sábado y domingo del fin de semana de d
        sab = d if d.weekday() == 5 else (d - timedelta(days=d.weekday()-5))
        dom = sab + timedelta(days=1)
        if str(sab) in feriados_set or str(dom) in feriados_set:
            return True
    return False


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


def _generar_fechas_por_ratio_diario(yyyy_mm: str, cantidad: int) -> list:
    """Distribuye `cantidad` reservas usando un ratio diario (7 pesos lun..dom).
    Se seleccionan días aleatoriamente ponderando por pesos diarios.
    """
    try:
        year, month = map(int, yyyy_mm.split('-'))
    except Exception:
        return []
    if cantidad <= 0:
        return []
    # Obtener pesos diarios (Lun..Dom)
    pesos_map = getattr(cfg, 'ratio_diario_por_mes', {}) or {}
    pesos_default = tuple(getattr(cfg, 'ratio_diario_default', (1, 1, 1, 1, 1, 1, 1)))
    pesos = tuple(pesos_map.get(yyyy_mm, pesos_default))
    if len(pesos) != 7:
        try:
            print(f"⚠️  {yyyy_mm}: ratio_diario tiene {len(pesos)} valores. Debe tener 7 (Lun..Dom). Se usará default.")
        except Exception:
            pass
        pesos = tuple(pesos_default)

    last_day = monthrange(year, month)[1]
    # Construir lista de días del mes con su peso (según weekday)
    dias = []
    pesos_dias = []
    for day in range(1, last_day + 1):
        d = datetime(year, month, day).date()
        w = d.weekday()  # 0=Mon..6=Sun
        p = int(pesos[w]) if w < len(pesos) else 1
        if p < 0:
            p = 0
        dias.append(d)
        pesos_dias.append(p)

    # Semilla opcional
    try:
        seed = getattr(cfg, 'random_seed', None)
        if seed is not None:
            random.seed(seed)
    except Exception:
        pass

    # Muestreo ponderado con reemplazo de `cantidad` días
    total_peso = sum(pesos_dias)
    if total_peso <= 0:
        return []
    probs = [p / total_peso for p in pesos_dias]
    escogidos = random.choices(dias, weights=probs, k=int(cantidad))

    # Construir datetimes con desempate por bloques de 10 minutos
    asignadas = []
    contador_por_dia = {}
    for d in escogidos:
        count = contador_por_dia.get(d, 0)
        minute = (count * 10) % 60
        asignadas.append(datetime(d.year, d.month, d.day, 12, minute, 0))
        contador_por_dia[d] = count + 1
    asignadas.sort()
    return asignadas


def _generar_fechas_por_ratio_festivo(yyyy_mm: str, cantidad: int) -> list:
    """Distribuye `cantidad` reservas ponderando festivo vs no festivo.
    Usa cfg.ratio_festivo_no_festivo_por_mes o cfg.ratio_festivo_no_festivo_default.
    """
    try:
        year, month = map(int, yyyy_mm.split('-'))
    except Exception:
        return []
    if cantidad <= 0:
        return []
    last_day = monthrange(year, month)[1]
    feriados_set = _build_feriados_set()
    marcar_finde = bool(getattr(cfg, 'marcar_fin_de_semana_con_feriado_como_festivo', True))

    festivos_dias = []
    nofestivos_dias = []
    for day in range(1, last_day + 1):
        d = datetime(year, month, day).date()
        if _es_festivo(d, feriados_set, marcar_finde):
            festivos_dias.append(d)
        else:
            nofestivos_dias.append(d)

    # Obtener ratio
    try:
        mapa = getattr(cfg, 'ratio_festivo_no_festivo_por_mes', {}) or {}
        defecto = tuple(getattr(cfg, 'ratio_festivo_no_festivo_default', (2, 5)))
        r = mapa.get(yyyy_mm, defecto)
        rf, rnf = int(r[0]), int(r[1])
    except Exception:
        rf, rnf = 2, 5
    base = max(rf + rnf, 1)

    # Calcular cuántas a festivo y no festivo
    cant_fest = round(cantidad * (rf / base))
    cant_nofest = int(cantidad) - cant_fest

    # Semilla
    try:
        seed = getattr(cfg, 'random_seed', None)
        if seed is not None:
            random.seed(seed)
    except Exception:
        pass

    # Elegir días al azar en cada grupo
    def asignar(dias: list, cant: int) -> list:
        if cant <= 0 or len(dias) == 0:
            return []
        escogidos = [random.choice(dias) for _ in range(cant)]
        asignadas = []
        contador = {}
        for d in escogidos:
            c = contador.get(d, 0)
            minute = (c * 10) % 60
            asignadas.append(datetime(d.year, d.month, d.day, 12, minute, 0))
            contador[d] = c + 1
        return asignadas

    fechas = asignar(festivos_dias, cant_fest) + asignar(nofestivos_dias, cant_nofest)
    fechas.sort()
    return fechas


def generar_fechas_para_mes(yyyy_mm: str, cantidad: int) -> list:
    """Distribuye `cantidad` reservas dentro del mes (YYYY-MM) según modo configurado.
    - 'semana_finde': respeta ratio semana/fin de semana.
    - 'diario': pondera por pesos diarios (7 valores Lun..Dom).
    - 'festivo': pondera por festivo vs no festivo (según feriados del país).
    """
    modo = str(getattr(cfg, 'modo_distribucion_dias', 'semana_finde') or 'semana_finde').lower()
    if modo == 'diario':
        return _generar_fechas_por_ratio_diario(yyyy_mm, int(cantidad))
    if modo == 'festivo' and bool(getattr(cfg, 'usar_distribucion_festivo', True)):
        return _generar_fechas_por_ratio_festivo(yyyy_mm, int(cantidad))

    if modo == 'diario_festivo':
        # Similar al diario, pero separando días normales vs festivos
        try:
            year, month = map(int, yyyy_mm.split('-'))
        except Exception:
            return []
        if cantidad <= 0:
            return []
        last_day = monthrange(year, month)[1]
        feriados_set = _build_feriados_set()
        marcar_finde = bool(getattr(cfg, 'marcar_fin_de_semana_con_feriado_como_festivo', True))
        # Pesos base
        conf_map = getattr(cfg, 'ratio_diario_festivo_por_mes', {}) or {}
        conf_default = getattr(cfg, 'ratio_diario_festivo_default', {}) or {}
        normal = tuple(conf_map.get(yyyy_mm, {}).get('normal', conf_default.get('normal', (1,1,1,1,1,1,1))))
        festivo = tuple(conf_map.get(yyyy_mm, {}).get('festivo', conf_default.get('festivo', (1,1,1,1,1,1,1))))
        if len(normal) != 7 or len(festivo) != 7:
            normal = tuple(conf_default.get('normal', (1,1,1,1,1,1,1)))
            festivo = tuple(conf_default.get('festivo', (1,1,1,1,1,1,1)))
        # Construir universo de fechas, y contenedores por weekday y por tipo (festivo/normal)
        dias_todos: list[datetime.date] = []
        is_festivo_flags: list[bool] = []
        weekdays: list[int] = []
        for day in range(1, last_day + 1):
            d = datetime(year, month, day).date()
            w = d.weekday()
            is_fest = _es_festivo(d, feriados_set, marcar_finde)
            dias_todos.append(d)
            weekdays.append(w)
            is_festivo_flags.append(is_fest)

        usar_cuota_fest = bool(getattr(cfg, 'usar_cuota_festivo_en_diario_festivo', True))

        def hamilton_round(targets: list[float], total_int: int) -> list[int]:
            base = [int(x) for x in targets]
            resto = total_int - sum(base)
            fracs = [(i, targets[i] - base[i]) for i in range(len(targets))]
            fracs.sort(key=lambda x: x[1], reverse=True)
            for i in range(max(0, resto)):
                base[fracs[i][0]] += 1
            return base

        asignadas: list[datetime] = []

        balancear = bool(getattr(cfg, 'balancear_por_semanas', False))

        if usar_cuota_fest and not balancear:
            try:
                mapa = getattr(cfg, 'ratio_festivo_no_festivo_por_mes', {}) or {}
                defecto = tuple(getattr(cfg, 'ratio_festivo_no_festivo_default', (2, 5)))
                rf, rnf = mapa.get(yyyy_mm, defecto)
                rf, rnf = int(rf), int(rnf)
                base_rf = max(rf + rnf, 1)
                cant_fest = round(int(cantidad) * (rf / base_rf))
                cant_nofest = int(cantidad) - cant_fest
            except Exception:
                cant_fest = int(cantidad) // 2
                cant_nofest = int(cantidad) - cant_fest

            # Para festivos: cupos por weekday usando pesos festivo
            fest_dias_by_w = {w: [] for w in range(7)}
            for d, w, isf in zip(dias_todos, weekdays, is_festivo_flags):
                if isf:
                    fest_dias_by_w[w].append(d)
            Wf = [len(fest_dias_by_w[w]) * max(0, int(festivo[w])) for w in range(7)]
            sumWf = sum(Wf)
            if sumWf > 0:
                targets = [cant_fest * (w / sumWf) for w in Wf]
                cupos_w = hamilton_round(targets, cant_fest)
            else:
                cupos_w = [0] * 7
            # Distribuir por weekday en round-robin sobre fechas de ese weekday
            for w in range(7):
                fechas_w = fest_dias_by_w[w]
                k = cupos_w[w]
                if not fechas_w or k <= 0:
                    continue
                cont_idx = 0
                cont_por_fecha = {d: 0 for d in fechas_w}
                for _ in range(k):
                    d = fechas_w[cont_idx % len(fechas_w)]
                    m = cont_por_fecha[d]
                    asignadas.append(datetime(d.year, d.month, d.day, 12, (m * 10) % 60, 0))
                    cont_por_fecha[d] = m + 1
                    cont_idx += 1

            # No festivos: cupos por weekday usando pesos normal
            nf_dias_by_w = {w: [] for w in range(7)}
            for d, w, isf in zip(dias_todos, weekdays, is_festivo_flags):
                if not isf:
                    nf_dias_by_w[w].append(d)
            Wn = [len(nf_dias_by_w[w]) * max(0, int(normal[w])) for w in range(7)]
            sumWn = sum(Wn)
            if sumWn > 0:
                targets = [cant_nofest * (w / sumWn) for w in Wn]
                cupos_w = hamilton_round(targets, cant_nofest)
            else:
                cupos_w = [0] * 7
            for w in range(7):
                fechas_w = nf_dias_by_w[w]
                k = cupos_w[w]
                if not fechas_w or k <= 0:
                    continue
                cont_idx = 0
                cont_por_fecha = {d: 0 for d in fechas_w}
                for _ in range(k):
                    d = fechas_w[cont_idx % len(fechas_w)]
                    m = cont_por_fecha[d]
                    asignadas.append(datetime(d.year, d.month, d.day, 12, (m * 10) % 60, 0))
                    cont_por_fecha[d] = m + 1
                    cont_idx += 1
        elif not usar_cuota_fest and not balancear:
            # Sin cuota festivo/no festivo: cupos por weekday considerando ambos tipos a la vez
            # Peso agregado por weekday = n_fest_w*festivo[w] + n_normal_w*normal[w]
            dias_by_w = {w: [] for w in range(7)}
            fest_by_w = {w: [] for w in range(7)}
            norm_by_w = {w: [] for w in range(7)}
            for d, w, isf in zip(dias_todos, weekdays, is_festivo_flags):
                dias_by_w[w].append(d)
                (fest_by_w if isf else norm_by_w)[w].append(d)
            W = []
            for w in range(7):
                W.append(len(fest_by_w[w]) * max(0, int(festivo[w])) + len(norm_by_w[w]) * max(0, int(normal[w])))
            sumW = sum(W)
            if sumW <= 0:
                return []
            targets = [int(cantidad) * (w / sumW) for w in W]
            cupos_w = hamilton_round(targets, int(cantidad))
            # distribuir cada cupo_w entre las fechas de ese weekday, alternando entre festivo/normal para respetar composición
            for w in range(7):
                k = cupos_w[w]
                if k <= 0 or not dias_by_w[w]:
                    continue
                # lista intercalada: prioriza festivos si hay pesos mayores
                pool = fest_by_w[w] + norm_by_w[w]
                if not pool:
                    continue
                cont_idx = 0
                cont_por_fecha = {d: 0 for d in pool}
                for _ in range(k):
                    d = pool[cont_idx % len(pool)]
                    m = cont_por_fecha[d]
                    asignadas.append(datetime(d.year, d.month, d.day, 12, (m * 10) % 60, 0))
                    cont_por_fecha[d] = m + 1
                    cont_idx += 1

        else:
            # Balanceo por semanas
            import calendar as _cal
            weeks_matrix = _cal.monthcalendar(year, month)  # filas: semanas, columnas: lun..dom (0 si fuera de mes)
            # Construir para cada semana su lista de fechas
            semanas_fechas = []
            for week in weeks_matrix:
                fechas_semana = []
                for idx, day in enumerate(week):
                    if day > 0:
                        fechas_semana.append(datetime(year, month, day).date())
                if fechas_semana:
                    semanas_fechas.append(fechas_semana)

            # Peso por semana = suma de pesos de sus días según festivo/normal y weekday
            pesos_semana = []
            detalle_semana = []
            for fechas_semana in semanas_fechas:
                ps = 0
                w_det = [0,0,0,0,0,0,0]
                for d in fechas_semana:
                    w = d.weekday()
                    isf = _es_festivo(d, feriados_set, marcar_finde)
                    val = (festivo[w] if isf else normal[w])
                    ps += val
                    w_det[w] += val
                pesos_semana.append(max(0, int(ps)))
                detalle_semana.append(w_det)
            sum_ps = sum(pesos_semana)
            if sum_ps <= 0:
                return []
            # Debug pesos por semana
            try:
                if bool(getattr(cfg, 'debug_pesos_semanales', False)):
                    semanas_txt = []
                    for i, fechas_semana in enumerate(semanas_fechas):
                        if not fechas_semana:
                            continue
                        rango = f"{fechas_semana[0].strftime('%d/%m')}–{fechas_semana[-1].strftime('%d/%m')}"
                        wtxt = ','.join(str(x) for x in detalle_semana[i])
                        print(f"peso_semana [{rango}] = {pesos_semana[i]} | por weekday [L..D]: {wtxt}")
            except Exception:
                pass
            # Cupos por semana (Hamilton)
            targets = [int(cantidad) * (ps / sum_ps) for ps in pesos_semana]
            cupos_sem = [int(x) for x in targets]
            resto = int(cantidad) - sum(cupos_sem)
            fracs = [(i, targets[i] - cupos_sem[i]) for i in range(len(targets))]
            fracs.sort(key=lambda x: x[1], reverse=True)
            for i in range(resto):
                cupos_sem[fracs[i][0]] += 1

            # Dentro de cada semana: repartir por weekday con pesos (festivo/normal) y RR por fechas del mismo weekday
            for fechas_semana, k_sem in zip(semanas_fechas, cupos_sem):
                if k_sem <= 0:
                    continue
                # Agrupar por weekday y tipo
                fest_by_w = {w: [] for w in range(7)}
                norm_by_w = {w: [] for w in range(7)}
                for d in fechas_semana:
                    w = d.weekday()
                    (fest_by_w if _es_festivo(d, feriados_set, marcar_finde) else norm_by_w)[w].append(d)
                # Peso por weekday en la semana
                W = [len(fest_by_w[w]) * max(0, int(festivo[w])) + len(norm_by_w[w]) * max(0, int(normal[w])) for w in range(7)]
                sumW = sum(W)
                if sumW <= 0:
                    continue
                # Asignación por D'Hondt: garantiza prioridad a weekdays con mayor peso
                cupos_w = [0] * 7
                for _ in range(k_sem):
                    best_idx = None
                    best_val = -1.0
                    for i_w in range(7):
                        if W[i_w] <= 0:
                            continue
                        val = W[i_w] / (cupos_w[i_w] + 1)
                        if val > best_val:
                            best_val = val
                            best_idx = i_w
                    if best_idx is None:
                        break
                    cupos_w[best_idx] += 1
                # Repartir cupos_w entre fechas de ese weekday (intercalando festivo/normal si ambos existen)
                for w in range(7):
                    k = cupos_w[w]
                    pool = fest_by_w[w] + norm_by_w[w]
                    if k <= 0 or not pool:
                        continue
                    cont_idx = 0
                    cont_por_fecha = {d: 0 for d in pool}
                    for _ in range(k):
                        d = pool[cont_idx % len(pool)]
                        m = cont_por_fecha[d]
                        asignadas.append(datetime(d.year, d.month, d.day, 12, (m * 10) % 60, 0))
                        cont_por_fecha[d] = m + 1
                        cont_idx += 1

        asignadas.sort()
        return asignadas

    # Default: semana/fin de semana
    year, month = map(int, yyyy_mm.split('-'))
    if cantidad <= 0:
        return []
    dias_semana, dias_finde = _dias_semana_y_finde(year, month)
    cant_semana, cant_finde = _calcular_asignacion_semana_finde(yyyy_mm, int(cantidad))
    fechas_semana = _asignar_aleatorio_en_dias(dias_semana, cant_semana, year, month, hora=12)
    fechas_finde = _asignar_aleatorio_en_dias(dias_finde, cant_finde, year, month, hora=12)
    fechas = sorted(fechas_semana + fechas_finde)
    return fechas


def generar_fechas_para_mes_por_semana(yyyy_mm: str, demanda_semanal: list) -> list:
    """Distribuye las reservas según vector semanal [w1, w2, ...].
    Las semanas se basan en el calendario (lunes a domingo) usando calendar.monthcalendar.
    Puede haber 4, 5 o 6 semanas en un mes; si entregas menos valores de los necesarios, se avisa por consola.
    """
    try:
        year, month = map(int, yyyy_mm.split('-'))
    except Exception:
        return []
    # Construir semanas reales del mes (lunes-domingo)
    import calendar as _cal
    weeks_matrix = _cal.monthcalendar(year, month)  # cada fila: [lun..dom], 0 = día fuera de mes
    semanas_dias = []
    for week in weeks_matrix:
        dias_semana = []
        for idx, day in enumerate(week):
            if day > 0:
                dias_semana.append(datetime(year, month, day).date())
        if dias_semana:
            semanas_dias.append(dias_semana)

    num_semanas = len(semanas_dias)
    counts = list(demanda_semanal or [])
    if len(counts) < num_semanas:
        print(f"⚠️  {yyyy_mm} tiene {num_semanas} semanas, pero entregaste {len(counts)} valores. Agrega el/los faltante(s).")
        # Rellenar con 0 para continuar
        counts = counts + [0] * (num_semanas - len(counts))
    elif len(counts) > num_semanas:
        print(f"ℹ️  {yyyy_mm}: se entregaron {len(counts)} valores, pero el mes tiene {num_semanas} semanas. Se ignorarán los extras.")
        counts = counts[:num_semanas]

    fechas = []
    for idx in range(len(semanas_dias)):
        dias = semanas_dias[idx]
        cantidad = int(counts[idx]) if idx < len(counts) else 0
        if cantidad <= 0 or len(dias) == 0:
            continue
        # Respetar ratio semana/fin de semana dentro de la semana
        dias_sem = [d for d in dias if d.weekday() < 5]
        dias_fin = [d for d in dias if d.weekday() >= 5]
        cant_sem, cant_fin = _calcular_asignacion_semana_finde(yyyy_mm, cantidad)
        fechas_sem = _asignar_aleatorio_en_dias(dias_sem, cant_sem, year, month, hora=12)
        fechas_fin = _asignar_aleatorio_en_dias(dias_fin, cant_fin, year, month, hora=12)
        fechas.extend(fechas_sem)
        fechas.extend(fechas_fin)
    fechas = sorted(fechas)
    # Debug: mostrar asignación por semana
    try:
        asignadas_por_semana = []
        for dias in semanas_dias:
            dias_set = set(dias)
            count = sum(1 for fdt in fechas if fdt.date() in dias_set)
            asignadas_por_semana.append(count)
        total_entregadas = sum(int(x) for x in counts)
        total_asignadas = sum(asignadas_por_semana)
        semanas_txt = ", ".join([
            f"[{dias[0].strftime('%d/%m')}–{dias[-1].strftime('%d/%m')}]" if len(dias) > 0 else "[]"
            for dias in semanas_dias
        ])
        print(f"🧮 {yyyy_mm}: semanas={num_semanas} ({semanas_txt}) | entregadas={counts} (total={total_entregadas}) | asignadas={asignadas_por_semana} (total={total_asignadas})")
        if total_asignadas != total_entregadas:
            print(f"‼️ {yyyy_mm}: MISMATCH total entregadas vs asignadas. Revisa el vector semanal o reporta este mensaje.")
    except Exception:
        pass
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
        base_val_raw = demanda_base[key]
        # Soportar demanda como entero o lista semanal
        if isinstance(base_val_raw, (list, tuple)):
            try:
                base_vec = [int(x) for x in list(base_val_raw)]
            except Exception:
                base_vec = [0]
            # Generar para cada año aplicando crecimiento a cada elemento
            for year in range(y + 1, hasta_anio + 1):
                new_key = f"{year:04d}-{m:02d}"
                years_elapsed = year - y
                factor = ((1.0 + tasa) ** years_elapsed)
                new_vec = [max(0, int(round(v * factor))) for v in base_vec]
                if new_key in demanda_base and not sobrescribir:
                    continue
                demanda_base[new_key] = new_vec
                added += 1
            continue
        else:
            base_val = int(base_val_raw)
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
        # Solo aplicar aleatoriedad a demandas enteras; listas semanales se respetan
        if isinstance(v, (list, tuple)):
            continue
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
    # Aleatoriedad solo si los valores son enteros; listas semanales se preservan
    demanda_map = aplicar_aleatoriedad_demanda(demanda_map)
    # Log de entrada para verificar formatos
    try:
        ejemplo = {k: (v if isinstance(v, int) else list(v) if isinstance(v, (list, tuple)) else v) for k, v in list(demanda_map.items())[:3]}
        print(f"📥 Demanda (muestra): {ejemplo}")
    except Exception:
        pass
    for yyyy_mm in sorted((demanda_map or {}).keys()):
        demanda = demanda_map[yyyy_mm]
        if isinstance(demanda, (list, tuple)):
            fechas = generar_fechas_para_mes_por_semana(yyyy_mm, list(demanda))
        else:
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

        # Resumen semanal de demanda (por semana calendario Lun-Dom)
        try:
            if len(fechas) > 0:
                from collections import defaultdict
                semanas = defaultdict(lambda: [0, 0, 0, 0, 0, 0, 0])
                for f in fechas:
                    d = f.date()
                    week_start = d - timedelta(days=d.weekday())  # lunes de esa semana
                    semanas[week_start][d.weekday()] += 1
                for semana_inicio in sorted(semanas.keys()):
                    conteos = tuple(semanas[semana_inicio])
                    print(f"semana ({semana_inicio.day}/{semana_inicio.month}/{semana_inicio.year}): {conteos}")
        except Exception:
            pass

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
                # Regla de ayudantes por día:
                # - 1 cliente => 1 ayudante (usa escala solitario si existe)
                # - >1 clientes => 2 ayudantes (usa escala general)
                pago = 0
                num_ayudantes_dia = 1 if cantidad == 1 else (2 if cantidad > 1 else 0)
                try:
                    escalas_solitario = list(getattr(cfg, 'pago_ayudante_escalas_solitario', []) or [])
                    escalas_solitario_sorted = sorted(escalas_solitario, key=lambda x: x[0])
                except Exception:
                    escalas_solitario_sorted = []

                if cantidad == 1 and len(escalas_solitario_sorted) > 0:
                    for umbral, monto in escalas_solitario_sorted:
                        if cantidad >= umbral:
                            pago = monto
                        else:
                            break
                    if pago == 0:
                        pago = escalas_solitario_sorted[0][1]
                else:
                    for umbral, monto in escalas_sorted:
                        if cantidad >= umbral:
                            pago = monto
                        else:
                            break
                    if pago == 0 and escalas_sorted:
                        pago = escalas_sorted[0][1]

                # Registrar una fila por ayudante para poder sumar por ayudante en el mes
                num = max(0, int(num_ayudantes_dia))
                for ayud_idx in range(1, num + 1):
                    registros_costos_op.append({
                        'fecha': datetime(dia.year, dia.month, dia.day, 20, 0, 0),
                        'email': cfg.email_placeholder,
                        'id_reserva': None,
                        'descripcion': 'pago extra ayudante (diario)',
                        'monto': float(pago),
                        'ayudantes_pagados': int(num_ayudantes_dia),
                        'pago_unitario': float(pago),
                        'ayudante': ayud_idx,
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


