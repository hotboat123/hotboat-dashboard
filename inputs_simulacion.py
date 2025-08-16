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

    '2025-08': 13,
    '2025-09': 16,
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
ticket_promedio = 150_000

# Costo operativo por cada reserva (CLP)
costo_variable_por_reserva = 45_000

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
    (1, 25_000),
    (2, 45_000),
    (3, 60_000),
    (4, 70_000),
    (5, 80_000),
    (6, 90_000),
    (7, 100_000),
]
# Si hay más reservas que el mayor umbral, se usa el último monto de la lista

# Gasto de marketing mensual (CLP)
gasto_marketing_mensual = 300_000

# Costo fijo mensual (CLP)
costo_fijo_mensual = 700_000

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
     '2026-01': (0, 5),  # ejemplo: marzo con 2:5
}

# Ratio por defecto si no se especifica uno por mes
ratio_semana_finde_default = (3, 4)  # 3 en semana, 4 en fin de semana (aprox 43% semana / 57% finde)

# Semilla opcional para reproducibilidad de la asignación aleatoria de días
# Establécela a un entero (por ejemplo 42) para resultados reproducibles; déjala en None para aleatorio puro
random_seed = 42

