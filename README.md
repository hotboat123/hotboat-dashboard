# HotBoat Dashboard System

Sistema completo de análisis y visualización de datos para HotBoat, incluyendo 3 dashboards especializados.

## 🚀 Instalación y Configuración

### Requisitos
```bash
pip install -r requirements.txt
```

## 🔄 **Diagrama del Flujo de Trabajo Completo**

```
📥 DATOS FUENTE (archivos_input/)
├── 📊 Datos bancarios (Banco Chile, Banco Estado, Mercado Pago)
├── 📅 Datos de Booknetic (Appointments, Payments)
└── 📢 Datos de marketing (Google Ads, Meta Ads)

    ↓
    ↓ PROCESAMIENTO DE DATOS
    ↓

🛠️ ARCHIVOS DE PROCESAMIENTO:
├── gastos_hotboat_sin_drive.py
│   └── Procesa datos financieros → archivos_output/gastos hotboat.csv
│
├── Informacion_reservas.py
│   └── Procesa datos de reservas → archivos_output/reservas_HotBoat.csv
│
└── estimacion_utilidad_hotboat.py
    └── Calcula utilidad → archivos_output/ingresos_totales.csv, costos_operativos.csv

    ↓
    ↓ DATOS PROCESADOS (archivos_output/)
    ↓

📊 ARCHIVOS CSV GENERADOS:
├── gastos hotboat.csv
├── abonos hotboat.csv
├── reservas_HotBoat.csv
├── ingresos_totales.csv
├── costos_operativos.csv
└── gastos_marketing.csv

    ↓
    ↓ VISUALIZACIÓN EN DASHBOARDS
    ↓

🚀 EJECUTOR PRINCIPAL:
└── ejecutar_todos_dashboards.py
    ├── Ejecuta reservas.py (puerto 8050)
    │   └── importa dashboards.py → crea app_reservas
    │
    ├── utilidad.py  
    │   └── importa dashboards.py → crea app_utilidad
    │
    └── marketing.py
        └── importa dashboard_marketing_simple.py → crea app_marketing
```

## 🏗️ **Estructura de Archivos Dashboard**

### 📁 **Archivos Ejecutores (Simples)**
```
reservas.py          → Importa desde dashboards.py → Crea app de reservas
utilidad.py          → Importa desde dashboards.py → Crea app de utilidad
marketing.py         → Importa desde dashboard_marketing_simple.py → Crea app de marketing
```

### 📁 **Archivos de Implementación (Completos)**
```
dashboards.py                    → Módulo principal con funciones para reservas y utilidad
dashboard_marketing_simple.py    → Dashboard completo de marketing (más de 1200 líneas)
```

## 🔍 **¿Por qué hay marketing.py Y dashboard_marketing_simple.py?**

### **Patrón de Diseño: Separación de Responsabilidades**

```
📁 PATRÓN: SEPARACIÓN DE RESPONSABILIDADES

┌─────────────────────────────────────┐
│           EJECUTORES                │
│  (Archivos simples - ~50-100 líneas)│
├─────────────────────────────────────┤
│ reservas.py                         │
│ utilidad.py                         │
│ marketing.py                        │
│                                     │
│ FUNCIÓN: Solo iniciar el servidor   │
│ y mostrar mensajes informativos     │
└─────────────────────────────────────┘
                    ↓
                    ↓ importa
                    ↓
┌─────────────────────────────────────┐
│        IMPLEMENTACIONES             │
│  (Archivos complejos - 1000+ líneas)│
├─────────────────────────────────────┤
│ dashboards.py                       │
│ dashboard_marketing_simple.py       │
│                                     │
│ FUNCIÓN: Toda la lógica del         │
│ dashboard, gráficos, callbacks      │
└─────────────────────────────────────┘
```

### **Ejemplo: marketing.py vs dashboard_marketing_simple.py**

#### **marketing.py** (Archivo Simple - 725 líneas)
```python
# marketing.py - SOLO EJECUTOR
from dashboard_marketing_simple import app

if __name__ == '__main__':
    print("📊 INICIANDO DASHBOARD DE MARKETING HOTBOAT...")
    print("============================================================")
    print("📈 Cargando datos de marketing...")
    print("📊 Dashboard de marketing con métricas CPC, CTR, región")
    print("🎯 Análisis de audiencias y tipos de anuncios")
    print("💹 Hook rates y conversiones")
    print("✅ Dashboard de marketing creado exitosamente")
    print("🌐 URL: http://localhost:8056")
    print("🔄 Para detener: Ctrl+C")
    print("============================================================")
    app.run(debug=False, port=8056)
```

#### **dashboard_marketing_simple.py** (Archivo Completo - 1254 líneas)
```python
# dashboard_marketing_simple.py - IMPLEMENTACIÓN COMPLETA
import dash
from dash import html, dcc, Input, Output, callback
import pandas as pd
import plotly.graph_objects as go
# ... más de 1200 líneas de código con:
# - Layout completo del dashboard
# - Callbacks para interactividad
# - Gráficos complejos
# - Filtros avanzados
# - Procesamiento de datos
```

## 🔄 **Flujo Completo de Ejecución**

### **1. Procesamiento de Datos:**
```bash
python gastos_hotboat_sin_drive.py
python Informacion_reservas.py  
python estimacion_utilidad_hotboat.py
```

### **2. Ejecución de Dashboards:**
```bash
python ejecutar_todos_dashboards.py
```

### **3. Lo que sucede internamente:**
```
ejecutar_todos_dashboards.py
    ↓
    ├── reservas.py
    │   └── importa dashboards.py → crea app_reservas
    │
    ├── utilidad.py  
    │   └── importa dashboards.py → crea app_utilidad
    │
    └── marketing.py
        └── importa dashboard_marketing_simple.py → crea app_marketing
```

## 🎯 **Ventajas de esta Estructura**

1. **Simplicidad**: Los ejecutores son simples y fáciles de entender
2. **Mantenibilidad**: La lógica compleja está separada
3. **Reutilización**: `dashboards.py` se usa para reservas y utilidad
4. **Flexibilidad**: Cada dashboard puede tener su propia implementación
5. **Debugging**: Fácil identificar dónde está el problema

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