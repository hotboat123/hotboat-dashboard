# Para actualizar data
1. Descargar movimientos facturados bco chile nacional e internacional
2. Descargar mov no facturados bco chile (opcional)
3. Revisar ultima fila de abonos bco estado y descargar chequera histórica desde esa fecha (pueden ser varios archivos)
4. Descargar info mercado pago --> Tu negocio - ventas - descargar Excel de ventas
5. Descargar Appointments y Payments de Booknetic
5. Subir toda esa info a carpeta "archivo_input" desde carpeta "descargas"
6. correr código "gastos_hotboat_sin_Drive.py"
6. correr código "Informacion_reservas.py"
7. correr código "analisis_gráficos.py"
8. abrir link 



# Dashboard de Reservas HotBoat

Dashboard interactivo para visualizar y analizar las reservas de HotBoat. Desarrollado con Dash y Plotly.

## Características

- Visualización de reservas por día, semana y mes
- Gráfico de horarios más populares
- Interfaz moderna con tema oscuro
- Métricas clave de reservas

## Requisitos

- Python 3.8+
- Dependencias listadas en `requirements.txt`

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/hotboat123/hotboat-dashboard.git
cd hotboat-dashboard
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Uso

1. Asegúrate de tener el archivo de datos `archivos/reservas_HotBoat.csv` en el directorio correcto.

2. Ejecutar el dashboard:
```bash
python dashboard_reservas.py
```

3. Abrir el navegador en `http://localhost:8050`

## Estructura del Proyecto

```
hotboat-dashboard/
├── archivos/
│   └── reservas_HotBoat.csv
├── dashboard_reservas.py
├── requirements.txt
└── README.md
```

## Licencia

Este proyecto está bajo la Licencia MIT. 