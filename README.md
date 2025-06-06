# 🚤 HotBoat - Sistema de Análisis de Datos Náuticos

Sistema integral de análisis de datos para operaciones marítimas de HotBoat, con dashboards interactivos y procesamiento automatizado de datos.

## 📁 Estructura del Proyecto

```
hotboat/
├── 🚤 hotboat_dashboards.py      ← ARCHIVO PRINCIPAL para dashboards
├── 🔄 hotboat_procesamiento.py   ← ARCHIVO PRINCIPAL para procesamiento
├── 📊 dashboards/                ← Sistema de dashboards
│   ├── core/                     ← Módulos optimizados
│   │   ├── dashboards_main.py    ← Dashboard consolidado principal
│   │   ├── data_loader.py        ← Carga unificada de datos
│   │   ├── chart_generators.py   ← Generación de gráficos
│   │   └── dashboard_components.py ← Componentes UI
│   ├── utilidad_optimizado.py    ← Dashboard de utilidad (Puerto 8055)
│   ├── reservas_optimizado.py    ← Dashboard de reservas (Puerto 8050)
│   ├── marketing_optimizado.py   ← Dashboard de marketing (Puerto 8056)
│   └── funciones/                ← Funciones auxiliares
├── 🔧 procesamiento/             ← Sistema de procesamiento
│   ├── Informacion_reservas.py   ← Procesamiento de reservas
│   ├── gastos_hotboat_sin_drive.py ← Procesamiento de gastos
│   ├── estimacion_utilidad_hotboat.py ← Estimaciones de utilidad
│   └── check_data.py             ← Validación de datos
├── 📥 archivos_input/            ← Datos de entrada
├── 📤 archivos_output/           ← Datos procesados
└── 🧪 tests/                     ← Sistema de testing
```

## 🚀 Inicio Rápido

### 1. Ejecutar Dashboards
```bash
# Dashboard específico
python hotboat_dashboards.py utilidad    # Puerto 8055
python hotboat_dashboards.py reservas    # Puerto 8050  
python hotboat_dashboards.py marketing   # Puerto 8056

# Todos los dashboards en paralelo
python hotboat_dashboards.py todos

# Menú interactivo
python hotboat_dashboards.py
```

### 2. Procesar Datos
```bash
# Proceso específico
python hotboat_procesamiento.py reservas
python hotboat_procesamiento.py gastos
python hotboat_procesamiento.py utilidad

# Todos los procesos en secuencia
python hotboat_procesamiento.py todos

# Menú interactivo
python hotboat_procesamiento.py
```

## 📊 Dashboards Disponibles

### 🔹 Dashboard de Utilidad Operativa (Puerto 8055)
- Análisis de ingresos y gastos operativos
- Métricas de utilidad y márgenes  
- Proyecciones financieras
- **URL:** http://localhost:8055

### 🔹 Dashboard de Reservas (Puerto 8050)
- Análisis de reservas y pagos
- Tendencias de ocupación
- Análisis de clientes
- **URL:** http://localhost:8050

### 🔹 Dashboard de Marketing (Puerto 8056)
- Métricas de campañas publicitarias
- Análisis de CPC, CTR y conversiones
- ROI por región y audiencia
- **URL:** http://localhost:8056

## 🔄 Procesamiento de Datos

### 1. **Información de Reservas**
- Procesa datos de reservas desde archivos Excel/CSV
- Genera archivos consolidados para análisis
- Valida integridad de datos de clientes

### 2. **Gastos Operativos**
- Procesamiento sin dependencia de Google Drive
- Categorización automática de gastos
- Generación de reportes financieros

### 3. **Estimaciones de Utilidad**
- Cálculos de utilidad operativa
- Proyecciones basadas en tendencias
- Análisis de rentabilidad por período

### 4. **Validación de Datos**
- Verificación de calidad de datos
- Detección de inconsistencias
- Limpieza automática de datasets

## 🧪 Sistema de Testing

```bash
# Ejecutar todos los tests
python -m pytest tests/ -v

# Tests específicos
python -m pytest tests/test_data_loading.py
python -m pytest tests/test_dashboard_outputs.py
python -m pytest tests/test_metrics_regression.py
```

## 📋 Requisitos

```bash
# Instalar dependencias principales
pip install -r requirements.txt

# Instalar dependencias de testing (opcional)
pip install -r requirements-testing.txt
```

**Dependencias principales:**
- pandas >= 1.3.0
- plotly >= 5.0.0
- dash >= 2.0.0
- openpyxl >= 3.0.0

## 🎯 Casos de Uso

### Para Análisis Diario
```bash
# 1. Procesar datos del día
python hotboat_procesamiento.py todos

# 2. Abrir dashboard de utilidad
python hotboat_dashboards.py utilidad
```

### Para Análisis de Marketing
```bash
# 1. Procesar datos de marketing
python hotboat_procesamiento.py marketing

# 2. Abrir dashboard de marketing
python hotboat_dashboards.py marketing
```

### Para Reportes Gerenciales
```bash
# 1. Generar estimaciones de utilidad
python hotboat_procesamiento.py utilidad

# 2. Abrir todos los dashboards
python hotboat_dashboards.py todos
```

## 🔧 Configuración Avanzada

### Puertos de Dashboards
Los puertos están predefinidos en `hotboat_dashboards.py`:
- Utilidad: 8055
- Reservas: 8050  
- Marketing: 8056

### Estructura de Datos
- **Input:** `archivos_input/` - Datos originales en Excel/CSV
- **Output:** `archivos_output/` - Datos procesados y listos para análisis
- **Tests:** `tests/test_data/` - Datos estáticos para testing

## 📈 Métricas y KPIs

### Utilidad Operativa
- Ingresos totales por reservas
- Costos operativos y fijos
- Margen de utilidad operativa
- Proyecciones financieras

### Reservas
- Tasa de ocupación
- Valor promedio por reserva
- Análisis de temporadas
- Perfil de clientes

### Marketing
- CPC (Costo por Click)
- CTR (Click Through Rate)  
- ROI por campaña
- Conversiones por región

## 🚀 Optimizaciones

### Arquitectura Modular
- **Antes:** 15+ archivos dispersos
- **Después:** 2 archivos principales + estructura organizada
- **Beneficios:** Mantenimiento simplificado, mejor organización

### Performance
- Carga optimizada de datos
- Cacheo inteligente en dashboards
- Procesamiento paralelo disponible

## 🆘 Solución de Problemas

### Dashboard no arranca
```bash
# Verificar que el puerto no esté ocupado
netstat -an | find "8055"

# Reiniciar con puerto diferente
python dashboards/utilidad_optimizado.py --port 8057
```

### Error de datos
```bash
# Validar estructura de datos
python hotboat_procesamiento.py validar

# Ver estado de archivos
python hotboat_procesamiento.py estado
```

### Problemas de importación
```bash
# Verificar estructura de directorios
python -c "from pathlib import Path; print([d.name for d in Path('.').iterdir() if d.is_dir()])"
```

## 📞 Soporte

Para problemas técnicos o consultas sobre el sistema HotBoat:
1. Revisar logs en consola
2. Ejecutar validación de datos
3. Verificar estructura de archivos
4. Consultar documentación específica en cada módulo

---

**🚤 HotBoat - Navegando hacia el éxito con datos inteligentes** 