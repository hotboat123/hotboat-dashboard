import pandas as pd
import os
import unicodedata
from funciones.funciones import leer_excel_banco_estado, ver_si_es_nacional_facturado, ver_si_es_nacional_no_facturado, leer_excel_mov_facturados_nacional, leer_excel_mov_no_facturados_nacional, leer_excel_mov_facturados_internacional, leer_excel_mov_no_facturados_internacional, leer_pdf
from funciones.funciones_reservas import procesar_fechas_reservas, procesar_appointments, procesar_reservas
# from analisis_graficos import graficar_reservas_por_dia_mes

# Inicializar variables
payments = None
appointments = None
df_reservas_original = None

# Leer archivos de input
for archivo in os.listdir('archivos_input/Archivos input reservas/'):
    ruta_archivo = os.path.join('archivos_input/Archivos input reservas/', archivo)
    if archivo.endswith(".csv"):
        df = pd.read_csv(ruta_archivo)
        if "payments" in archivo:
            payments = df
        elif "appointments" in archivo:
            appointments = df
        elif "reservas_HotBoat" in archivo:
            df_reservas_original = procesar_fechas_reservas(df)

# Procesar las nuevas reservas
df_reservas_nuevas = procesar_appointments(payments, appointments)

# Procesar todas las reservas
df_reservas = procesar_reservas(df_reservas_original, df_reservas_nuevas)

# Asegurar que 'Customer' exista y esté poblado en la versión normal antes de crear la versión Meta
try:
    if 'ID' in df_reservas.columns:
        # Crear columna si no existe
        if 'Customer' not in df_reservas.columns:
            df_reservas['Customer'] = ''
        # Completar vacíos desde df_reservas_nuevas si está disponible
        if 'Customer' in df_reservas_nuevas.columns:
            mapping_customer = df_reservas_nuevas.set_index('ID')['Customer']
            mask_vacio = df_reservas['Customer'].isna() | (df_reservas['Customer'].astype(str).str.strip() == '')
            df_reservas.loc[mask_vacio, 'Customer'] = df_reservas.loc[mask_vacio, 'ID'].map(mapping_customer)
            try:
                completados = df_reservas.loc[mask_vacio, 'Customer'].notna().sum()
                print(f"👥 'Customer' completado desde nuevas reservas para {completados} filas vacías.")
            except Exception:
                pass
except Exception as e:
    print(f"⚠️ No se pudo completar 'Customer' desde nuevas reservas: {e}")

df_reservas_meta = df_reservas.copy()

# Ajustes para formato de Offline Conversions (Meta)
# 1) Normalizar teléfonos para que todos comiencen con "+"
try:
    phone_col_candidates = ["Phone Number_2", "telefono", "teléfono", "telefono (Phone Number_2)"]
    phone_col = next((c for c in phone_col_candidates if c in df_reservas_meta.columns), None)
    if phone_col:
        serie_telefonos = df_reservas_meta[phone_col]
        def ensure_plus(valor):
            if pd.isna(valor):
                return valor
            s = str(valor).strip()
            if s == "":
                return s
            return s if s.startswith("+") else "+" + s
        needs_plus = serie_telefonos.apply(lambda v: pd.notna(v) and str(v).strip() != "" and not str(v).strip().startswith("+"))
        df_reservas_meta.loc[needs_plus, phone_col] = serie_telefonos.loc[needs_plus].apply(ensure_plus)
        try:
            print(f"☎️ Teléfonos normalizados: {needs_plus.sum()} agregados con '+'. Columna usada: {phone_col}")
        except Exception:
            pass
    else:
        print("⚠️ No se encontró columna de teléfono (ej. 'Phone Number_2').")
except Exception as e:
    print(f"❌ Error normalizando teléfonos: {e}")

# 2) Re-formatear fecha_hora_creacion_reserva a ISO 8601 con Z (YYYY-MM-DDTHH:MM:SSZ) para versión Meta
try:
    fecha_col = "fecha_hora_creacion_reserva"
    if fecha_col in df_reservas_meta.columns:
        fechas_dt = pd.to_datetime(df_reservas_meta[fecha_col], errors="coerce", dayfirst=True)
        # Formato ISO 8601 con sufijo Z (asumiendo hora local sin conversión de zona)
        formatted_iso = fechas_dt.dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        df_reservas_meta[fecha_col] = formatted_iso.where(fechas_dt.notna(), df_reservas_meta[fecha_col])
        n_convertidas = fechas_dt.notna().sum()
        n_invalidas = fechas_dt.isna().sum()
        print(f"🗓️ Fechas formateadas: {n_convertidas} OK, {n_invalidas} no convertidas.")
    else:
        print("⚠️ No se encontró columna 'fecha_hora_creacion_reserva'.")
except Exception as e:
    print(f"❌ Error formateando fechas: {e}")

# 3) Dividir 'Customer' en nombre(s) y apellido(s): nombre, segundo nombre, apellido, segundo apellido
try:
    customer_col = "Customer"
    if customer_col in df_reservas_meta.columns:
        def strip_accents(texto):
            try:
                return ''.join(c for c in unicodedata.normalize('NFKD', str(texto)) if not unicodedata.combining(c))
            except Exception:
                return str(texto)

        def normalize_capitalization(texto):
            if pd.isna(texto) or str(texto).strip() == "":
                return ""
            # Capitalizar cada palabra correctamente (maneja guiones simples separándolos por espacio)
            return " ".join([strip_accents(p).capitalize() for p in str(texto).split()])

        def split_customer(nombre_completo):
            if pd.isna(nombre_completo):
                return pd.Series({
                    "nombre": "",
                    "segundo nombre": "",
                    "apellido": "",
                    "segundo apellido": "",
                })
            partes = str(nombre_completo).strip().split()
            if len(partes) == 0:
                return pd.Series({
                    "nombre": "",
                    "segundo nombre": "",
                    "apellido": "",
                    "segundo apellido": "",
                })
            if len(partes) == 1:
                return pd.Series({
                    "nombre": normalize_capitalization(partes[0]),
                    "segundo nombre": "",
                    "apellido": "",
                    "segundo apellido": "",
                })
            if len(partes) == 2:
                return pd.Series({
                    "nombre": normalize_capitalization(partes[0]),
                    "segundo nombre": "",
                    "apellido": normalize_capitalization(partes[1]),
                    "segundo apellido": "",
                })
            if len(partes) == 3:
                return pd.Series({
                    "nombre": normalize_capitalization(partes[0]),
                    "segundo nombre": "",
                    "apellido": normalize_capitalization(partes[1]),
                    "segundo apellido": normalize_capitalization(partes[2]),
                })
            # 4 o más palabras: tomar 1er y 2do como nombres, y las dos últimas como apellidos
            return pd.Series({
                "nombre": normalize_capitalization(partes[0]),
                "segundo nombre": normalize_capitalization(partes[1]),
                "apellido": normalize_capitalization(partes[-2]),
                "segundo apellido": normalize_capitalization(" ".join(partes[-1:])),
            })

        nombres_df = df_reservas_meta[customer_col].apply(split_customer)
        df_reservas_meta = pd.concat([df_reservas_meta.drop(columns=[customer_col]), nombres_df], axis=1)
        try:
            # Métrica básica de longitudes
            lens = df_reservas_meta[["nombre", "segundo nombre", "apellido", "segundo apellido"]].fillna("").agg(lambda s: s.str.len() > 0).sum(axis=1)
            print(f"👤 Columnas de nombre creadas. 'Customer' reemplazado por 4 columnas. Registros: {len(df_reservas_meta)}")
        except Exception:
            pass
    else:
        print("⚠️ No se encontró columna 'Customer' para dividir en nombres.")
except Exception as e:
    print(f"❌ Error creando columnas de nombre: {e}")

# 4) Restaurar formato de fecha en versión normal (DD/MM/YYYY HH:MM:SS) para 'fecha_hora_creacion_reserva'
try:
    fecha_col_norm = "fecha_hora_creacion_reserva"
    if fecha_col_norm in df_reservas.columns:
        fechas_dt_norm = pd.to_datetime(df_reservas[fecha_col_norm], errors="coerce", dayfirst=True)
        formatted_norm = fechas_dt_norm.dt.strftime("%d/%m/%Y %H:%M:%S")
        df_reservas[fecha_col_norm] = formatted_norm.where(fechas_dt_norm.notna(), df_reservas[fecha_col_norm])
        print("🕒 Formato de fecha de compra restaurado en versión normal (DD/MM/YYYY HH:MM:SS).")
    else:
        print("⚠️ No se encontró columna 'fecha_hora_creacion_reserva' en versión normal.")
except Exception as e:
    print(f"❌ Error restaurando formato de fecha en versión normal: {e}")

# Guardar el DataFrame en un archivo CSV
df_reservas.to_csv("archivos_input/Archivos input reservas/reservas_HotBoat.csv", index=False)
df_reservas.to_csv("archivos_output/reservas_HotBoat.csv", index=False)

# Exportar versión específica para Meta Offline Conversions
df_reservas_meta.to_csv("archivos_input/Archivos input reservas/reservas_hotboat_version_meta.csv", index=False)
df_reservas_meta.to_csv("archivos_output/reservas_hotboat_version_meta.csv", index=False)

# Generar gráfico de reservas por día y mes
# graficar_reservas_por_dia_mes(df_reservas)