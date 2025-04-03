# una que otra modificación

from google.auth import default
from google.colab import auth
from google.colab import sheets
from google.colab import files
from google.colab import drive
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import pandas as pd
nombre_hoja_reservas = "Gastos HotBoat"

# Ruta del archivo en la carpeta 'downloads' (ajusta el nombre del archivo)
payments_path = "/content/drive/My Drive/payments_2025Mar01.csv"
appointments_path = "/content/drive/My Drive/appointments_2025Mar01.csv"


# Montar Google Drive (si el archivo está en Drive)
drive.mount('/content/drive')

auth.authenticate_user()

creds, _ = default()

gc = gspread.authorize(creds)


# Abrir por titulo
sh = gc.open("VAN Hotboat")
