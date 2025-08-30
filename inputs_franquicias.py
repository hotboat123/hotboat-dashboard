#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuración de simulación para franquicias HotBoat.

Cómo funciona (alto nivel):
- Se toma una demanda base por mes desde inputs_simulacion.demanda_por_mes (y su expansión si está activa).
- Para cada franquicia, se ajusta la demanda por:
  - Número de HotBoats de esa franquicia
  - Factor de estacionalidad según el mes (verano/invierno/normal)
  - Fecha de apertura: meses anteriores no cuentan
- Ingresos = demanda_ajustada * ticket_promedio (desde inputs_simulacion)
- Costos del franquiciado: arriendo mensual + costo variable por reserva
- Royalties: porcentaje de las ventas para el dueño de la marca (este archivo)

Resultado:
- Se calcula el royalty total, utilidades de cada franquicia y cuántas franquicias
  se necesitan (clonando una de referencia) para superar un objetivo de CLP.
"""

# Tasa de royalty (dueño de la marca recibe este % de las ventas)
royalty_rate = 0.10 # 9% (ajustable)

# Objetivo de royalty total (CLP) a superar
objetivo_royalty_total = 500_000_000

# Meses considerados como verano o invierno para la estacionalidad
# Si no defines estos, se usarán los de inputs_simulacion (si existen)
meses_verano = [1, 2]
meses_invierno = [7]

# Costo variable por reserva (del franquiciado). Si es None, se toma de inputs_simulacion.
costo_variable_por_reserva_franquicia = None

# Define aquí tus franquicias.
# - n_hotboats: número de HotBoats que operará la franquicia
# - estacionalidad: factores para Verano/Invierno/normal
# - apertura: 'YYYY-MM' a partir de cuando empieza a vender
# - arriendo_mensual: costo de arriendo mensual (CLP)

franquicias = {
    'Franquicia 1': {
        'n_hotboats': 2,
        'estacionalidad': {
            'Verano': 1.10,   # vende 10% más que el input base
            'Invierno': 1.00, # igual que base
            'normal': 1.00,   # no vende fuera de estación
        },
        'apertura': '2027-05',
        'arriendo_mensual': 1_000_000,
    },
    'Franquicia 2': {
        'n_hotboats': 2,
        'estacionalidad': {
            'Verano': 1.50,   # vende 10% más que el input base
            'Invierno': 1.50, # igual que base
            'normal': 1.50,   # no vende fuera de estación
        },
        'apertura': '2026-05',
        'arriendo_mensual': 500_000,
    },
}

# Franquicia de referencia para replicar (si deseas estimar cuántas iguales necesitas)
nombre_franquicia_modelo = 'Franquicia 1'

# Año objetivo para evaluar royalties (solo ese año). Si es None, se usa el último año disponible.
objetivo_anio = 2030  # Ej: 2028

# Número de iteraciones Monte Carlo para promediar resultados
simulaciones_num_iter = 100


# Escenario de aperturas de franquicias por año (para simular ingreso de la marca)
# Clona la `nombre_franquicia_modelo` con estos años de apertura y cantidades
# Ejemplo: {2027: 2, 2028: 4, 2029: 7, 2030: 10}
ingresos_marca_schedule = {
    2027: 2,
    2028: 4,
    2029: 7,
    2030: 10,
}

# Mes de apertura por defecto para clones del schedule (1=enero)
apertura_mes_default = 1


