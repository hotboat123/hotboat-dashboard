import pandas as pd

archivos = [
    ("archivos_output/reservas_HotBoat.csv", "OUTPUT"),
    ("archivos_input/Archivos input reservas/reservas_HotBoat.csv", "INPUT PROD"),
    ("archivos_input_tst/reservas_HotBoat.csv", "INPUT TEST")
]

for ruta, nombre in archivos:
    try:
        df = pd.read_csv(ruta)
        print(f"=== {nombre} ===")
        print(f"Archivo: {ruta}")
        print(f"Filas: {len(df)}")
        print(f"Emails únicos: {df['Customer Email'].nunique()}")
        print(f"Primeros 5 emails: {df['Customer Email'].head(5).tolist()}")
        print()
    except Exception as e:
        print(f"Error leyendo {nombre}: {e}\n") 