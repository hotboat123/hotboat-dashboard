import subprocess
import requests
import time

def check_port(port):
    try:
        response = requests.get(f"http://localhost:{port}", timeout=2)
        return f"✅ Puerto {port}: FUNCIONA (Status: {response.status_code})"
    except:
        return f"❌ Puerto {port}: NO RESPONDE"

def check_processes():
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        python_processes = [line for line in lines if 'python.exe' in line]
        return f"🐍 Procesos Python activos: {len(python_processes)}"
    except:
        return "❌ Error verificando procesos"

print("=== ESTADO DE DASHBOARDS HOTBOAT ===")
print(check_processes())
print(check_port(8050))  # Reservas
print(check_port(8055))  # Utilidad  
print(check_port(8056))  # Marketing
print("=====================================") 