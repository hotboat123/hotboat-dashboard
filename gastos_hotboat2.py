from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# Autenticación
gauth = GoogleAuth()
# Esto abrirá una ventana en el navegador para iniciar sesión
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

# Descargar un archivo específico (ID del archivo en Drive)
file_id = "https://docs.google.com/spreadsheets/d/1FFfkoi6SW0mtiicpyXnEPfWUprVTKGLGqqMQF2ep2Hk/edit?usp=drive_link"
archivo = drive.CreateFile({'id': file_id})
archivo.GetContentFile("archivo.xlsx")

# https: // docs.google.com/spreadsheets/d/1FFfkoi6SW0mtiicpyXnEPfWUprVTKGLGqqMQF2ep2Hk/edit?usp = drive_link
print("Archivo descargado con éxito")
