# HotBoat Dashboard System

Sistema completo de análisis y visualización de datos para HotBoat, incluyendo 3 dashboards especializados.

## 🚀 Instalación y Configuración

### Requisitos
```bash
pip install -r requirements.txt
```

### Estructura de Archivos (NUEVA ORGANIZACIÓN)

#### 📁 Archivos Principales (Raíz del proyecto)
```
├── ejecutar_todos_dashboards.py    # 🔥 PRINCIPAL: Ejecutor múltiple de todos los dashboards
├── Informacion_reservas.py         # Procesamiento de datos de reservas
├── inputs_modelo.py                # Configuraciones y parámetros del modelo
├── gastos_hotboat_sin_drive.py     # Procesamiento de gastos financieros
├── estimacion_utilidad_hotboat.py  # Cálculo de utilidad operativa
├── dashboards.py                   # Módulo principal con funciones de dashboard
├── reservas.py                     # Ejecutor del dashboard de reservas
├── utilidad.py                     # Ejecutor del dashboard de utilidad operativa  
├── marketing.py                    # Ejecutor del dashboard de marketing
├── funciones/                      # Componentes y utilidades
├── archivos_output/                # Datos procesados (CSV)
└── archivos_input/                 # Datos fuente
```

#### 📁 Archivos Secundarios (archivos_secundarios/)
```
├── dashboard_*.py                  # Versiones anteriores de dashboards
├── capturar_dashboards_*.py        # Scripts de captura de screenshots
├── analisis_graficos.py            # Análisis de gráficos independiente
├── check_*.py                      # Scripts de verificación
├── debug_*.py                      # Scripts de depuración
├── test_*.py                       # Scripts de prueba
└── gastos_hotboat_sin_drive antiguo.py  # Versión anterior del procesador
```

## 📊 Dashboards Disponibles

### 1. Dashboard de Reservas
- **Puerto:** 8050
- **URL:** http://localhost:8050
- **Características:**
  - Análisis de reservas por periodo
  - Métricas de ocupación
  - Gráficos de tendencias temporales
  - Análisis de horas populares

### 2. Dashboard de Utilidad Operativa
- **Puerto:** 8055  
- **URL:** http://localhost:8055
- **Características:**
  - Cálculo de utilidad operativa
  - Análisis de ingresos vs costos
  - Comparación de variables financieras
  - Insights automáticos de rentabilidad

### 3. Dashboard de Marketing
- **Puerto:** 8056
- **URL:** http://localhost:8056  
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

### 🔥 PRINCIPAL: Ejecutar Todos Simultáneamente (Recomendado)
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

## 📈 Procesamiento de Datos

### Flujo de Trabajo Completo
1. **Descargar datos bancarios** (Banco Chile, Banco Estado, Mercado Pago)
2. **Descargar datos de Booknetic** (Appointments y Payments)
3. **Subir archivos a `archivos_input/`**
4. **Ejecutar procesamiento:**
   ```bash
   python gastos_hotboat_sin_drive.py
   python Informacion_reservas.py
   python estimacion_utilidad_hotboat.py
   ```
5. **Ejecutar dashboards:**
   ```bash
   python ejecutar_todos_dashboards.py
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
✅ **ORGANIZACIÓN** - Estructura limpia y organizada

## 🚀 Ejecutor Múltiple de Dashboards

### `ejecutar_todos_dashboards.py`

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

## 📁 Estructura del Proyecto

```
hotboat-dashboard/
├── 📁 Archivos Principales
│   ├── ejecutar_todos_dashboards.py    # 🚀 PRINCIPAL
│   ├── Informacion_reservas.py         # 📊 Procesamiento reservas
│   ├── inputs_modelo.py                # ⚙️ Configuraciones
│   ├── gastos_hotboat_sin_drive.py     # 💰 Procesamiento gastos
│   ├── estimacion_utilidad_hotboat.py  # 📈 Cálculo utilidad
│   ├── dashboards.py                   # 🏗️ Módulo principal
│   ├── reservas.py                     # 🎯 Dashboard reservas
│   ├── utilidad.py                     # 💼 Dashboard utilidad
│   └── marketing.py                    # 📢 Dashboard marketing
├── 📁 archivos_secundarios/            # 🔧 Archivos de desarrollo
├── 📁 funciones/                       # 🛠️ Utilidades y componentes
├── 📁 archivos_output/                 # 📊 Datos procesados
├── 📁 archivos_input/                  # 📥 Datos fuente
├── 📁 archivos_input_tst/              # 🧪 Datos de prueba
├── 📁 tests/                           # 🧪 Pruebas
├── 📁 graficos/                        # 📈 Gráficos exportados
├── requirements.txt                    # 📦 Dependencias
├── README.md                           # 📖 Documentación
└── NAVEGACION_DASHBOARDS.md           # 🧭 Guía de navegación
```

## 🎯 Archivos Esenciales

### Para Ejecutar Dashboards:
1. `ejecutar_todos_dashboards.py` - **PRINCIPAL**
2. `dashboards.py` - Módulo base
3. `reservas.py`, `utilidad.py`, `marketing.py` - Ejecutores

### Para Procesar Datos:
1. `gastos_hotboat_sin_drive.py` - Procesamiento financiero
2. `Informacion_reservas.py` - Procesamiento reservas
3. `estimacion_utilidad_hotboat.py` - Cálculo utilidad
4. `inputs_modelo.py` - Configuraciones

### Para Desarrollo:
- Carpeta `archivos_secundarios/` - Versiones anteriores y herramientas
- Carpeta `funciones/` - Componentes reutilizables 