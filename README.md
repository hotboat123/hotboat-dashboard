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



# Dashboard HotBoat

Sistema completo de análisis y visualización de datos para HotBoat, incluyendo 3 dashboards especializados.

## 🚀 Instalación y Configuración

### Requisitos
```bash
pip install -r requirements.txt
```

### Estructura de Archivos
```
├── dashboards.py                  # Módulo principal con funciones de dashboard
├── dashboard_utilidad.py          # Dashboard específico de marketing/utilidad
├── reservas.py                   # Ejecutor del dashboard de reservas
├── utilidad.py                   # Ejecutor del dashboard de utilidad operativa  
├── marketing.py                  # Ejecutor del dashboard de marketing
├── ejecutar_todos_dashboards.py  # 🔥 NUEVO: Ejecutor múltiple de todos los dashboards
├── funciones/                    # Componentes y utilidades
├── archivos_output/              # Datos procesados (CSV)
└── archivos_input/               # Datos fuente
```

## 📊 Dashboards Disponibles

### 1. Dashboard de Reservas
- **Puerto:** 8050
- **URL:** http://localhost:8050
- **Ejecutar:** `python reservas.py`
- **Características:**
  - Análisis de reservas por periodo
  - Métricas de ocupación
  - Gráficos de tendencias temporales
  - Análisis de horas populares

### 2. Dashboard de Utilidad Operativa
- **Puerto:** 8055  
- **URL:** http://localhost:8055
- **Ejecutar:** `python utilidad.py`
- **Características:**
  - Cálculo de utilidad operativa
  - Análisis de ingresos vs costos
  - Comparación de variables financieras
  - Insights automáticos de rentabilidad

### 3. Dashboard de Marketing
- **Puerto:** 8056
- **URL:** http://localhost:8056  
- **Ejecutar:** `python marketing.py`
- **Características:**
  - Análisis detallado de gastos de marketing
  - ROI de campañas publicitarias
  - Correlación marketing vs ingresos
  - Optimización de presupuesto

## 🎯 Navegación Entre Dashboards

Todos los dashboards incluyen una barra de navegación superior que permite cambiar fácilmente entre:
- **Reservas** → Análisis operativo
- **Utilidad Operativa** → Análisis financiero integral  
- **Marketing** → Análisis de marketing y ROI

## 🔧 Uso Rápido

### 🔥 NUEVO: Ejecutar Todos Simultáneamente (Recomendado)
```bash
# Un solo comando que ejecuta los 3 dashboards
python ejecutar_todos_dashboards.py
```

### Ejecutar Individualmente
```bash
# Dashboard de Reservas
python reservas.py

# Dashboard de Utilidad Operativa  
python utilidad.py

# Dashboard de Marketing
python marketing.py
```

## 📈 Datos Requeridos

Los dashboards requieren los siguientes archivos en `archivos_output/`:
- `reservas_HotBoat.csv`
- `ingresos_totales.csv`
- `costos_operativos.csv`
- `gastos_marketing.csv`
- `abonos hotboat.csv`
- `gastos hotboat.csv`

## 🔄 Estado del Proyecto

✅ **FUNCIONAL** - Todos los dashboards están operativos
✅ **NAVEGACIÓN** - Sistema de navegación integrado
✅ **DATOS** - Carga automática de todos los archivos CSV
✅ **VISUALIZACIÓN** - Gráficos interactivos con Plotly

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

## 🚀 Ejecutor Múltiple de Dashboards

### Nuevo: `ejecutar_todos_dashboards.py`

Este archivo ejecuta automáticamente los 3 dashboards simultáneamente usando multiprocessing:

**Características:**
- ✅ Ejecuta todos los dashboards con un solo comando
- ✅ Manejo automático de procesos múltiples
- ✅ Verificación de archivos antes de ejecutar
- ✅ Detención limpia con Ctrl+C
- ✅ URLs de acceso mostradas automáticamente
- ✅ Compatible con Windows, Linux y macOS

**Uso:**
```bash
python ejecutar_todos_dashboards.py
```

**Salida esperada:**
```
🚤🚤🚤🚤🚤🚤🚤🚤🚤🚤🚤🚤🚤🚤🚤🚤🚤🚤🚤🚤
🚤 HOTBOAT DASHBOARDS - EJECUTOR MÚLTIPLE
🚤🚤🚤🚤🚤🚤🚤🚤🚤🚤🚤🚤🚤🚤🚤🚤🚤🚤🚤🚤

📊 Iniciando todos los dashboards simultáneamente...
============================================================
🚀 Iniciando Dashboard de Reservas en puerto 8050...
✅ Dashboard de Reservas iniciado
🚀 Iniciando Dashboard de Utilidad Operativa en puerto 8055...
✅ Dashboard de Utilidad Operativa iniciado
🚀 Iniciando Dashboard de Marketing en puerto 8056...
✅ Dashboard de Marketing iniciado
============================================================
🎉 TODOS LOS DASHBOARDS INICIADOS EXITOSAMENTE
============================================================

📱 URLs de acceso:
   🔗 Dashboard de Reservas: http://localhost:8050
   🔗 Dashboard de Utilidad Operativa: http://localhost:8055
   🔗 Dashboard de Marketing: http://localhost:8056

🔄 Para detener todos los dashboards: Ctrl+C
⚡ Para navegar entre dashboards, usa los enlaces en la interfaz web
============================================================
```

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