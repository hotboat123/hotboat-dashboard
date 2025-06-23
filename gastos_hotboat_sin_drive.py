#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚤 PROCESADOR DE GASTOS Y COSTOS HOTBOAT
========================================

Este script procesa los archivos financieros principales de HotBoat:
- Archivos de Banco Estado (Chequera)
- Archivos de Banco Chile (Movimientos Facturados)

Funciones:
1. Lee y procesa archivos Excel
2. Categoriza gastos automáticamente
3. Consolida datos de múltiples fuentes
4. Exporta archivos procesados para dashboards

Uso:
    python gastos_hotboat_sin_drive.py
"""

import sys
import pandas as pd
import os

# Importar la función principal de procesamiento
from funciones.funciones import procesar_archivos_financieros, leer_cartola_cuenta_corriente

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
        # Ejecutar el procesamiento principal
        success = procesar_archivos_financieros(
            directorio_input=DIRECTORIO_INPUT,
            directorio_output=DIRECTORIO_OUTPUT,
            valor_aproximado_dolar=VALOR_APROXIMADO_DOLAR,
            año_para_fecha_banco_estado=AÑO_PARA_FECHA_BANCO_ESTADO,
            diccionario_categorias=diccionario_categorias,
            descripciones_a_eliminar=descripciones_a_eliminar,
            diccionario_categoria_1=diccionario_categoria_1
        )
        
        # === PROCESAR ARCHIVOS DE CUENTA CORRIENTE ===
        cuenta_corriente_cargos = []
        cuenta_corriente_abonos = []
        for archivo in os.listdir(DIRECTORIO_INPUT):
            if archivo.lower().startswith('cartola') and archivo.lower().endswith(('.xls', '.xlsx')):
                ruta = os.path.join(DIRECTORIO_INPUT, archivo)
                try:
                    cargos, abonos = leer_cartola_cuenta_corriente(ruta)
                    if not cargos.empty:
                        cuenta_corriente_cargos.append(cargos)
                        print(f"✅ Procesado cargos cuenta corriente: {archivo} ({len(cargos)} filas)")
                    if not abonos.empty:
                        cuenta_corriente_abonos.append(abonos)
                        print(f"✅ Procesado abonos cuenta corriente: {archivo} ({len(abonos)} filas)")
                except Exception as e:
                    print(f"❌ Error procesando cuenta corriente {archivo}: {str(e)}")
        
        # Consolidar cargos y abonos de cuenta corriente
        df_cargos_cc = pd.DataFrame()
        df_abonos_cc = pd.DataFrame()
        
        if cuenta_corriente_cargos:
            df_cargos_cc = pd.concat(cuenta_corriente_cargos, ignore_index=True)
            df_cargos_cc = df_cargos_cc.drop_duplicates(subset=['Fecha', 'Descripción', 'Monto'], keep='first')
            print(f"📊 Cargos cuenta corriente consolidados: {len(df_cargos_cc)} filas")
            
        if cuenta_corriente_abonos:
            df_abonos_cc = pd.concat(cuenta_corriente_abonos, ignore_index=True)
            df_abonos_cc = df_abonos_cc.drop_duplicates(subset=['Fecha', 'Descripción', 'Monto'], keep='first')
            print(f"📊 Abonos cuenta corriente consolidados: {len(df_abonos_cc)} filas")
        
        # === INTEGRAR CON ARCHIVOS PRINCIPALES ===
        print("=" * 60)
        print("🔄 INTEGRANDO DATOS DE CUENTA CORRIENTE...")
        
        # Leer archivos principales existentes
        gastos_path = os.path.join(DIRECTORIO_OUTPUT, 'gastos hotboat.csv')
        abonos_path = os.path.join(DIRECTORIO_OUTPUT, 'abonos hotboat.csv')
        
        # Integrar cargos de cuenta corriente a gastos
        if os.path.exists(gastos_path) and not df_cargos_cc.empty:
            df_gastos = pd.read_csv(gastos_path)
            df_gastos_final = pd.concat([df_gastos, df_cargos_cc], ignore_index=True)
            df_gastos_final = df_gastos_final.drop_duplicates(subset=['Fecha', 'Descripción', 'Monto'], keep='first')
            df_gastos_final.to_csv(gastos_path, index=False)
            print(f"✅ Cargos cuenta corriente integrados a gastos hotboat.csv ({len(df_cargos_cc)} filas agregadas)")
        
        # Integrar abonos de cuenta corriente a abonos
        if os.path.exists(abonos_path) and not df_abonos_cc.empty:
            df_abonos = pd.read_csv(abonos_path)
            df_abonos_final = pd.concat([df_abonos, df_abonos_cc], ignore_index=True)
            df_abonos_final = df_abonos_final.drop_duplicates(subset=['Fecha', 'Descripción', 'Monto'], keep='first')
            df_abonos_final.to_csv(abonos_path, index=False)
            print(f"✅ Abonos cuenta corriente integrados a abonos hotboat.csv ({len(df_abonos_cc)} filas agregadas)")
        
        # Exportar archivos separados de cuenta corriente (opcional, para referencia)
        if not df_cargos_cc.empty:
            df_cargos_cc.to_csv(os.path.join(DIRECTORIO_OUTPUT, 'cuenta_corriente_cargos.csv'), index=False)
            print(f"💾 Archivo de referencia: cuenta_corriente_cargos.csv ({len(df_cargos_cc)} filas)")
        if not df_abonos_cc.empty:
            df_abonos_cc.to_csv(os.path.join(DIRECTORIO_OUTPUT, 'cuenta_corriente_abonos.csv'), index=False)
            print(f"💾 Archivo de referencia: cuenta_corriente_abonos.csv ({len(df_abonos_cc)} filas)")
        
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

