#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚤 PROCESADOR DE GASTOS Y COSTOS HOTBOAT
========================================

Este script procesa los archivos financieros principales de HotBoat:
- Archivos de Banco Estado (Chequera)
- Archivos de Banco Chile (Movimientos Facturados)
- Archivos de Cuenta Corriente (Cartolas)

Funciones:
1. Lee y procesa archivos Excel
2. Categoriza gastos automáticamente
3. Consolida datos de múltiples fuentes
4. Integra datos de cuenta corriente automáticamente
5. Exporta archivos procesados para dashboards

Uso:
    python gastos_hotboat_sin_drive.py
"""

import sys
import pandas as pd
import os

# Configurar UTF-8 para que los emojis funcionen siempre
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    # Para versiones de Python < 3.7
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

# Importar la función principal de procesamiento
from funciones.funciones import procesar_archivos_financieros

# Importar configuraciones
from inputs_modelo import diccionario_categorias, descripciones_a_eliminar, diccionario_categoria_1

# ======== CONFIGURACIÓN ========
VALOR_APROXIMADO_DOLAR = 950
AÑO_PARA_FECHA_BANCO_ESTADO = '2025'
DIRECTORIO_INPUT = 'archivos_input/archivos_input_costos'
DIRECTORIO_OUTPUT = 'archivos_output'

# ======== EJECUCIÓN PRINCIPAL ========
if __name__ == '__main__':
    try:
        # Ejecutar el procesamiento principal (incluye cuenta corriente)
        success = procesar_archivos_financieros(
            directorio_input=DIRECTORIO_INPUT,
            directorio_output=DIRECTORIO_OUTPUT,
            valor_aproximado_dolar=VALOR_APROXIMADO_DOLAR,
            año_para_fecha_banco_estado=AÑO_PARA_FECHA_BANCO_ESTADO,
            diccionario_categorias=diccionario_categorias,
            descripciones_a_eliminar=descripciones_a_eliminar,
            diccionario_categoria_1=diccionario_categoria_1
        )
        
        if success:
            print("🎉 ¡Procesamiento completado exitosamente!")
        else:
            print("❌ Error en el procesamiento")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Procesamiento interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        sys.exit(1)

