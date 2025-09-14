#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parámetros de simulación para utilidad operativa

Edita este archivo para configurar tu simulación. Valores por defecto incluidos.

Definiciones:
- demanda_por_mes: dict YYYY-MM -> número de clientes (reservas) en el mes
- ticket_promedio: valor CLP por reserva (ingreso por cliente)
- costo_variable_por_reserva: costo CLP por cada reserva (operativo)
- gasto_marketing_mensual: gasto fijo mensual en marketing
- costo_fijo_mensual: costo fijo mensual (arriendo, sueldos, etc.)

Puedes agregar tantos meses como quieras en el diccionario demanda_por_mes.
"""

# Mapea cada mes con su demanda estimada (número de clientes)
# demanda_por_mes = {
#     # Ejemplos, edítalos libremente:
#     '2025-08': 13,
#     '2025-09': 16,
#     '2025-10': 15,
#     '2025-11': 15,
#     '2025-12': 20,
#     '2026-01': 60,
#     '2026-02': 80,
#     '2026-03': 20,
#     '2026-04': 20, 
#     '2026-05': 20,
#     '2026-06': 10,
#     '2026-07': 35,
#     '2026-08': 15,
#     '2026-09': 18,
#     '2026-10': 18,
#     '2026-11': 28,
# }

demanda_por_mes = {
    # Nuevas demandas para probar:
    '2025-08': 16, ## ESTO ES POR SEMANA (FUNCIONA) [3,2,4,5,5]
    '2025-09': 20,##  (TAMBIEN FUNCIONA)
    '2025-10': 15,
    '2025-11': 20,
    '2025-12': 25,
    '2026-01': 120,
    '2026-02': 130,
    '2026-03': 20,
    '2026-04': 20, 
    '2026-05': 20,
    '2026-06': 15,
    '2026-07': 40,
    '2026-08': 20,
    '2026-09': 25,
    '2026-10': 20,
    '2026-11': 30,
    '2026-12': 35
}

# Ingreso promedio por cliente (CLP)
ticket_promedio = 160_000

# Costo operativo por cada reserva (CLP)
costo_variable_por_reserva = 45_000 #se usa para las franquicias, lo intentare arreglar

# Desglose opcional del costo operativo por reserva.
# Si se activa y se define el dict, se generará una fila por componente por cada reserva.
usar_desglose_costos_operativos = True
costo_operativo_detalle_por_reserva = {
    'leña': 1_500,
    'agua': 700,
    'luz': 520,
    'gas': 10_000,
}

# Pago del ayudante escalonado por día según número de reservas ese día
usar_pago_ayudante_escalonado = True
# Lista de tuplas: (cantidad_reservas, pago_diario)
pago_ayudante_escalas = [
    (1, 20_000),
    (2, 40_000),
    (3, 55_000),
    (4, 70_000),
    (5, 85_000),
    (6, 95_000),
    (7, 105_000),
]
# Si hay más reservas que el mayor umbral, se usa el último monto de la lista

# Escala especial cuando hay exactamente 1 cliente en el día y solo se necesita 1 ayudante.
# Si está definida y no vacía, en días con 1 reserva se usará esta escala en vez de `pago_ayudante_escalas`
# y se pagará a 1 solo ayudante (ignora `numero_ayudantes` ese día).
# Formato: lista de tuplas (cantidad_reservas, pago_diario). Normalmente basta con (1, monto).
pago_ayudante_escalas_solitario = [
    (1, 25_000),  # ejemplo: con 1 cliente, pagar $30.000 a 1 ayudante
]

# Número de ayudantes (cada uno recibe el pago según la escala)
numero_ayudantes = 2

# Gasto de marketing mensual (CLP)
gasto_marketing_mensual = 300_000

# Costo fijo mensual (CLP)
costo_fijo_mensual = 456_926

# Costo fijo estacional (verano vs invierno)
# Si activas `usar_costo_fijo_estacional`, se usará un costo distinto para los meses definidos como verano o invierno.
usar_costo_fijo_estacional = True
costo_fijo_mensual_verano = 635_000  # SUBE A 500 EL ARRIENDO
costo_fijo_mensual_invierno = 456_926 ## 300 ARRIENDO, 30 AGUA, 35 INTERNET +??
# Por defecto: verano = dic-ene-feb; invierno = jun-jul-ago. Puedes modificar estas listas.
meses_verano = [1, 2]
meses_invierno = [7]

# Texto que aparecerá en los CSV simulados
descripcion_ingreso = "Ingreso simulado por reserva"
descripcion_costo_operativo = "Costo operativo simulado por reserva"
descripcion_marketing = "Gasto marketing mensual simulado"
descripcion_costo_fijo = "Costo fijo mensual simulado"

# Identificadores opcionales (no son usados por el consolidado, pero ayudan a mantener estructura)
email_placeholder = "sim@hotboat.cl"
id_reserva_base = 1_000_000  # base para generar IDs únicos en la simulación


# Configuración de distribución semana / fin de semana por mes
# Formato: {'YYYY-MM': (reservas_semana, reservas_finde)}
# Ejemplo: en marzo 2 a 5 => de cada 7 reservas, 2 en semana y 5 en fin de semana
# Si un mes no está presente en este dict, se usará el valor por defecto de abajo.
ratio_semana_finde_por_mes = {
    # '2026-03': (2, 5),  # ejemplo: marzo con 2:5
    # '2026-01': (0, 5),  # ejemplo: marzo con 2:5
}

#
# Semilla opcional para reproducibilidad de la asignación aleatoria de días
# Establécela a un entero (por ejemplo 42) para resultados reproducibles; déjala en None para aleatorio puro
random_seed = 48

# Crecimiento anual de demanda (simulación de años posteriores)
# Si activas `expandir_demanda_con_crecimiento`, el sistema generará meses futuros
# hasta `simular_hasta_anio`, multiplicando la demanda base de cada mes por
# (1 + tasa_crecimiento_anual)^(años_transcurridos). No sobrescribe meses ya presentes
# salvo que `sobrescribir_demanda_existente_con_crecimiento` sea True.
expandir_demanda_con_crecimiento = True
tasa_crecimiento_anual = 0.10  # SOLO INFLUYE EN LA DEMANDA, NO EN LOS COSTOS
simular_hasta_anio = 2032 # Generar datos hasta este año (inclusive)
sobrescribir_demanda_existente_con_crecimiento = False

# Escenarios de simulación de demanda (multiplicadores)
# Puedes editar los factores aquí para cada escenario
escenarios_demanda = {
    'pesimista': 0.6,
    'normal': 1.0,
    'optimista': 1.3
}

# Control para ejecutar (o no) el simulador de escenarios (pesimista/normal/optimista)
# Si es False, el script simular_escenarios_utilidad.py saldrá sin ejecutar escenarios
ejecutar_escenarios_demanda = False

#Configuración en inputs_simulacion.py (opcional):
optimizar_pagos_config = {
    'alphas': [0.6, 0.8, 1.0],
    'base_invierno': [300_000, 300_000, 300_000],
    'base_verano':   [700_000, 700_000, 700_000],
    'piso_invierno': [2_000_000, 2_250_000, 3_000_000],
    'piso_verano':   [3_000_000, 3_350_000, 4_000_000],
    'escenarios': ['pesimista','normal','optimista'],  # o ['pesimista','normal','optimista']
}

# Aleatoriedad de demanda mensual (uniforme alrededor de la media definida)
# Si activas `usar_aleatoriedad_demanda`, por cada mes se muestrea una demanda
# desde Uniforme([(1-rango)*demanda, (1+rango)*demanda]) y se redondea a entero.
usar_aleatoriedad_demanda = False
demanda_uniforme_rango_pct = 0.3  # 20% → [0.8x, 1.2x]






#festivos 

# Modo de distribución de días para reservas cuando la demanda es un entero
# Opciones:
#  - 'semana_finde': usa ratio_semana_finde_por_mes / ratio_semana_finde_default
#  - 'diario': usa ratio_diario_por_mes / ratio_diario_default (7 pesos lun..dom)
#  - 'festivo': usa ratio_festivo_no_festivo_* (2 pesos festivo/no)
#  - 'diario_festivo': usa pesos por día (lun..dom) diferenciando normal/festivo
modo_distribucion_dias = 'diario_festivo'

# Opcion 1:
#  Ratio por defecto si no se especifica uno por mes
ratio_semana_finde_default = (60, 83)  # 3 en semana, 4 en fin de semana (aprox 43% semana / 57% finde)

# Opcion 2:
# Ratio diario por defecto (Lun..Dom) cuando modo_distribucion_dias = 'diario'
# Ejemplo pedido: (lunes, martes, miércoles, jueves, viernes, sábado, domingo)
# ratio_diario_default = (12, 14, 14, 20, 31, 26, 26)


# Opcion 3:
# Pesos por día diferenciando Normal vs Festivo cuando modo_distribucion_dias = 'diario_festivo'
# Estructura: {'normal': tuple7_lun_a_dom, 'festivo': tuple7_lun_a_dom}
ratio_diario_festivo_default = {
    'normal':  (12, 15, 15, 20, 31, 26, 26),
    'festivo': (27, 17, 27, 40, 40, 41, 40),
}

# Overrides por mes (YYYY-MM -> {'normal': tuple7, 'festivo': tuple7})
ratio_diario_festivo_por_mes = {
    # '2026-01': {
    #     'normal':  (10, 10, 12, 18, 30, 28, 25),
    #     'festivo': (14, 14, 16, 20, 36, 42, 40),
    # },
}

# País de feriados a usar para clasificar fechas ("Chile" o "Argentina")
pais_festivos = 'Chile'

# Activar modo de distribución por tipo de fecha (festivo vs no festivo)
# Para usarlo, establece: modo_distribucion_dias = 'festivo'
usar_distribucion_festivo = True

# Ratio festivo vs no festivo por mes (opcional): {'YYYY-MM': (festivo, no_festivo)}
ratio_festivo_no_festivo_por_mes = {
    # '2025-09': (2, 5),
}



# Considerar como festivo todo el fin de semana si Sábado o Domingo caen en feriado (true recomendado)
marcar_fin_de_semana_con_feriado_como_festivo = False

# Para modo 'diario_festivo': usar primero cuota festivo vs no festivo
# según ratio_festivo_no_festivo_* antes de distribuir por día de la semana
usar_cuota_festivo_en_diario_festivo = True
# Ratio festivo vs no festivo por defecto
ratio_festivo_no_festivo_default = (1, 1)

# Para modo 'diario_festivo': asignación determinística (sin aleatoriedad)
# respeta proporciones por pesos y ajusta con método de mayores restos
asignacion_deterministica_en_diario_festivo = True

# Para modo 'diario_festivo': balancear por semanas (cada semana calendario recibe cupos
# proporcionales a sus pesos y luego se reparte por weekday dentro de la semana)
balancear_por_semanas = True

# Debug: imprimir peso total por semana y desglose por weekday al simular
debug_pesos_semanales = False

# Feriados CHILE (2025)
feriados_chile_2025 = [
    '2025-04-17',  # Viernes Santo
    '2025-04-18',  # Viernes Santousar_cuota_festivo_en_diario_festivo 
    '2025-04-19',  # Viernes Santo
    '2025-04-20',  # Viernes Santo
    '2025-04-21',  # Viernes Santo
    '2025-05-01',  # Día del Trabajo
    '2025-05-02',  # Día del Trabajo
    '2025-05-03',  # Día del Trabajo
    '2025-05-04',  # Día del Trabajo
    '2025-05-05',  # Día del Trabajo
    '2025-05-21',  # Glorias Navales
    '2025-06-20',  # Pueblos Indígenas
    '2025-08-15',  # Asunción de la Virgen
    '2025-08-16',  # Asunción de la Virgen
    '2025-08-17',  # Asunción de la Virgen
    '2025-08-18',  # Asunción de la Virgen
    '2025-09-18',  # Independencia (irrenunciable)
    '2025-09-19',  # Glorias del Ejército (irrenunciable)
    '2025-09-20',
    '2025-09-21',
    '2025-09-22',
    '2025-10-12',  # Encuentro de Dos Mundos
    '2025-10-31',  # Iglesias Evangélicas y Protestantes
    '2025-11-01',  # Todos los Santos
    '2025-12-08',  # Inmaculada Concepción
    '2025-12-25',  # Navidad (irrenunciable)
]

# Feriados ARGENTINA (2025)
feriados_argentina_2025 = [
    '2025-01-01',  # Año Nuevo
    '2025-03-03',  # Carnaval
    '2025-03-04',  # Carnaval
    '2025-03-24',  # Memoria, Verdad y Justicia
    '2025-04-02',  # Malvinas
    '2025-04-18',  # Viernes Santo
    '2025-05-01',  # Día del Trabajo
    '2025-05-25',  # Revolución de Mayo
    '2025-06-16',  # Güemes (observado)
    '2025-06-20',  # Belgrano
    '2025-07-09',  # Independencia
    '2025-08-17',  # San Martín
    '2025-10-12',  # Diversidad Cultural
    '2025-11-24',  # Soberanía Nacional (observado)
    '2025-12-08',  # Inmaculada Concepción
    '2025-12-25',  # Navidad
]

# Años a considerar para feriados automáticos
feriados_anos = [2025, 2026, 2027]

# Listas extra manuales (se suman si no se puede generar automáticamente con librería)
feriados_chile_extra_2026 = [
    '2026-01-01', '2026-05-01', '2026-05-21', '2026-07-16', '2026-08-15',
    '2026-09-18', '2026-09-19', '2026-10-12', '2026-10-31', '2026-11-01',
    '2026-12-08', '2026-12-25',
]
feriados_chile_extra_2027 = [
    '2027-01-01', '2027-05-01', '2027-05-21', '2027-07-16', '2027-08-15',
    '2027-09-18', '2027-09-19', '2027-10-12', '2027-10-31', '2027-11-01',
    '2027-12-08', '2027-12-25',
]
feriados_argentina_extra_2026 = [
    '2026-01-01', '2026-03-24', '2026-04-02', '2026-05-01', '2026-05-25',
    '2026-06-20', '2026-07-09', '2026-08-17', '2026-10-12', '2026-11-20',
    '2026-12-08', '2026-12-25',
]
feriados_argentina_extra_2027 = [
    '2027-01-01', '2027-03-24', '2027-04-02', '2027-05-01', '2027-05-25',
    '2027-06-20', '2027-07-09', '2027-08-17', '2027-10-12', '2027-11-20',
    '2027-12-08', '2027-12-25',
]

# Intentar generar feriados automáticamente usando la librería 'holidays' si está disponible
try:
    # Construir por año para asegurar cobertura; si un año no está en la librería, usar extras
    cl_all = []
    ar_all = []
    for _year in feriados_anos:
        try:
            try:
                from holidays import Chile as _Chile
                _cl_set = _Chile(years=_year)
            except Exception:
                import holidays as _pyhol
                _cl_set = _pyhol.country_holidays(country='CL', years=_year)
            cur = sorted({d.strftime('%Y-%m-%d') for d in _cl_set.keys()})
        except Exception:
            cur = []
        if not cur:
            if _year == 2026:
                cur = list(feriados_chile_extra_2026)
            elif _year == 2027:
                cur = list(feriados_chile_extra_2027)
            else:
                cur = list(feriados_chile_2025)
        cl_all.extend(cur)

        try:
            try:
                from holidays import Argentina as _Argentina
                _ar_set = _Argentina(years=_year)
            except Exception:
                import holidays as _pyhol
                _ar_set = _pyhol.country_holidays(country='AR', years=_year)
            cur = sorted({d.strftime('%Y-%m-%d') for d in _ar_set.keys()})
        except Exception:
            cur = []
        if not cur:
            if _year == 2026:
                cur = list(feriados_argentina_extra_2026)
            elif _year == 2027:
                cur = list(feriados_argentina_extra_2027)
            else:
                cur = list(feriados_argentina_2025)
        ar_all.extend(cur)

    feriados_chile = sorted(set(cl_all))
    feriados_argentina = sorted(set(ar_all))
except Exception:
    # Fallback sin librería: usar listas 2025 + extras
    feriados_chile = sorted(set(
        feriados_chile_2025 + feriados_chile_extra_2026 + feriados_chile_extra_2027
    ))
    feriados_argentina = sorted(set(
        feriados_argentina_2025 + feriados_argentina_extra_2026 + feriados_argentina_extra_2027
    ))
