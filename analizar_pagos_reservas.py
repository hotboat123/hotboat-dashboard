import pandas as pd
import numpy as np

def analizar_pagos_reservas():
    """
    Analiza las diferencias entre PAID AMOUNT y TOTAL AMOUNT en las reservas
    """
    try:
        # Leer el archivo de reservas
        df_reservas = pd.read_csv('archivos_output/reservas_HotBoat.csv')
        print(f"📊 Analizando {len(df_reservas)} reservas...")
        
        # Verificar que las columnas existan
        if 'PAID AMOUNT' not in df_reservas.columns:
            print("❌ Error: No se encontró la columna 'PAID AMOUNT'")
            print(f"Columnas disponibles: {list(df_reservas.columns)}")
            return
        
        if 'TOTAL AMOUNT' not in df_reservas.columns:
            print("❌ Error: No se encontró la columna 'TOTAL AMOUNT'")
            print(f"Columnas disponibles: {list(df_reservas.columns)}")
            return
        
        # Convertir a numérico si es necesario
        df_reservas['PAID AMOUNT'] = pd.to_numeric(df_reservas['PAID AMOUNT'], errors='coerce')
        df_reservas['TOTAL AMOUNT'] = pd.to_numeric(df_reservas['TOTAL AMOUNT'], errors='coerce')
        
        # Calcular diferencias
        df_reservas['DIFERENCIA'] = df_reservas['TOTAL AMOUNT'] - df_reservas['PAID AMOUNT']
        df_reservas['PORCENTAJE_PAGADO'] = (df_reservas['PAID AMOUNT'] / df_reservas['TOTAL AMOUNT'] * 100).round(2)
        
        # Estadísticas generales
        print("\n" + "="*60)
        print("📈 ESTADÍSTICAS GENERALES")
        print("="*60)
        
        print(f"💰 Total reservas: {len(df_reservas):,}")
        print(f"💰 Total facturado: ${df_reservas['TOTAL AMOUNT'].sum():,.0f}")
        print(f"💰 Total pagado: ${df_reservas['PAID AMOUNT'].sum():,.0f}")
        print(f"💰 Total pendiente: ${df_reservas['DIFERENCIA'].sum():,.0f}")
        print(f"💰 Porcentaje pagado promedio: {df_reservas['PORCENTAJE_PAGADO'].mean():.1f}%")
        
        # Análisis por categorías
        print("\n" + "="*60)
        print("📊 ANÁLISIS POR CATEGORÍAS")
        print("="*60)
        
        # Reservas completamente pagadas
        completamente_pagadas = df_reservas[df_reservas['DIFERENCIA'] == 0]
        print(f"✅ Completamente pagadas: {len(completamente_pagadas):,} ({len(completamente_pagadas)/len(df_reservas)*100:.1f}%)")
        
        # Reservas parcialmente pagadas
        parcialmente_pagadas = df_reservas[(df_reservas['DIFERENCIA'] > 0) & (df_reservas['PAID AMOUNT'] > 0)]
        print(f"⚠️  Parcialmente pagadas: {len(parcialmente_pagadas):,} ({len(parcialmente_pagadas)/len(df_reservas)*100:.1f}%)")
        
        # Reservas sin pago
        sin_pago = df_reservas[df_reservas['PAID AMOUNT'] == 0]
        print(f"❌ Sin pago: {len(sin_pago):,} ({len(sin_pago)/len(df_reservas)*100:.1f}%)")
        
        # Reservas con sobrepago
        sobrepago = df_reservas[df_reservas['DIFERENCIA'] < 0]
        print(f"🔄 Con sobrepago: {len(sobrepago):,} ({len(sobrepago)/len(df_reservas)*100:.1f}%)")
        
        # Ejemplos de cada categoría
        print("\n" + "="*60)
        print("🔍 EJEMPLOS POR CATEGORÍA")
        print("="*60)
        
        if len(completamente_pagadas) > 0:
            print("\n✅ EJEMPLO - Completamente pagada:")
            ejemplo = completamente_pagadas.iloc[0]
            print(f"   ID: {ejemplo['ID']} | Total: ${ejemplo['TOTAL AMOUNT']:,.0f} | Pagado: ${ejemplo['PAID AMOUNT']:,.0f}")
        
        if len(parcialmente_pagadas) > 0:
            print("\n⚠️  EJEMPLO - Parcialmente pagada:")
            ejemplo = parcialmente_pagadas.iloc[0]
            print(f"   ID: {ejemplo['ID']} | Total: ${ejemplo['TOTAL AMOUNT']:,.0f} | Pagado: ${ejemplo['PAID AMOUNT']:,.0f} | Pendiente: ${ejemplo['DIFERENCIA']:,.0f}")
        
        if len(sin_pago) > 0:
            print("\n❌ EJEMPLO - Sin pago:")
            ejemplo = sin_pago.iloc[0]
            print(f"   ID: {ejemplo['ID']} | Total: ${ejemplo['TOTAL AMOUNT']:,.0f} | Pagado: ${ejemplo['PAID AMOUNT']:,.0f} | Pendiente: ${ejemplo['DIFERENCIA']:,.0f}")
        
        if len(sobrepago) > 0:
            print("\n🔄 EJEMPLO - Con sobrepago:")
            ejemplo = sobrepago.iloc[0]
            print(f"   ID: {ejemplo['ID']} | Total: ${ejemplo['TOTAL AMOUNT']:,.0f} | Pagado: ${ejemplo['PAID AMOUNT']:,.0f} | Sobrepago: ${abs(ejemplo['DIFERENCIA']):,.0f}")
        
        # Top 10 reservas con mayor pendiente
        print("\n" + "="*60)
        print("🔝 TOP 10 - MAYOR PENDIENTE")
        print("="*60)
        
        top_pendiente = df_reservas[df_reservas['DIFERENCIA'] > 0].nlargest(10, 'DIFERENCIA')
        for idx, row in top_pendiente.iterrows():
            print(f"   ID: {row['ID']} | Total: ${row['TOTAL AMOUNT']:,.0f} | Pagado: ${row['PAID AMOUNT']:,.0f} | Pendiente: ${row['DIFERENCIA']:,.0f}")
        
        # Distribución de porcentajes de pago
        print("\n" + "="*60)
        print("📊 DISTRIBUCIÓN DE PORCENTAJES DE PAGO")
        print("="*60)
        
        bins = [0, 25, 50, 75, 90, 100, float('inf')]
        labels = ['0-25%', '25-50%', '50-75%', '75-90%', '90-100%', '100%+']
        
        df_reservas['RANGO_PAGO'] = pd.cut(df_reservas['PORCENTAJE_PAGADO'], bins=bins, labels=labels, include_lowest=True)
        distribucion = df_reservas['RANGO_PAGO'].value_counts().sort_index()
        
        for rango, cantidad in distribucion.items():
            porcentaje = cantidad / len(df_reservas) * 100
            print(f"   {rango}: {cantidad:,} reservas ({porcentaje:.1f}%)")
        
        # Guardar análisis detallado
        df_analisis = df_reservas[['ID', 'TOTAL AMOUNT', 'PAID AMOUNT', 'DIFERENCIA', 'PORCENTAJE_PAGADO']].copy()
        df_analisis.to_csv('archivos_output/analisis_pagos_reservas.csv', index=False)
        print(f"\n💾 Análisis detallado guardado en: archivos_output/analisis_pagos_reservas.csv")
        
    except Exception as e:
        print(f"❌ Error al analizar pagos: {str(e)}")

if __name__ == "__main__":
    analizar_pagos_reservas() 