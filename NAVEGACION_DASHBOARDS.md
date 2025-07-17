# 🚤 Sistema de Navegación HotBoat Dashboards

## 📊 Dashboards Disponibles

### 1. Dashboard de Reservas
- **Puerto:** 8050
- **URL:** http://localhost:8050
- **Comando:** `python reservas.py`
- **Contenido:** Análisis de reservas, tendencias temporales, horas populares

### 2. Dashboard de Utilidad Operativa  
- **Puerto:** 8055
- **URL:** http://localhost:8055
- **Comando:** `python utilidad.py`
- **Contenido:** Ingresos, costos operativos, gastos marketing, utilidad neta

### 3. Dashboard de Marketing
- **Puerto:** 8056
- **URL:** http://localhost:8056
- **Comando:** `python marketing.py`
- **Contenido:** CPC, CTR, análisis regional, hook rates, conversiones

### 4. Dashboard de Gastos de Marketing
- **Puerto:** 8057
- **URL:** http://localhost:8057
- **Comando:** `python dashboard_gastos_marketing.py`
- **Contenido:** Comparación Google Ads vs Meta, evolución temporal, distribución por días, heatmap

### 5. Dashboard de Google Ads 🔥 NUEVO
- **Puerto:** 8058
- **URL:** http://localhost:8058
- **Comando:** `python dashboard_google_ads.py`
- **Contenido:** Análisis completo de campañas, palabras clave, dispositivos, demografía, series temporales

## 🔄 Navegación Entre Dashboards

### Características de Navegación:
- **Header Unificado:** Todos los dashboards comparten el mismo header con navegación
- **Estado Activo:** El dashboard actual se muestra destacado en la barra de navegación
- **Enlaces Directos:** Puedes hacer clic en cualquier dashboard para cambiar instantáneamente
- **Diseño Responsive:** La navegación funciona en desktop y móvil

### Barra de Navegación:
```
🚤 HotBoat Dashboards:
[Reservas] [Utilidad Operativa] [Marketing] [Gastos Marketing] [Google Ads]
```

- **Dashboard Activo:** Se muestra con fondo destacado y borde brillante
- **Otros Dashboards:** Se muestran como botones con hover effect
- **Transiciones Suaves:** Cambios con efectos CSS suaves

## �� Inicio Rápido

### 🔄 **Opción 0: Actualización Completa (🆕 NUEVO - Recomendado para Actualización)**
```bash
# Ejecuta TODO el flujo: procesamiento + dashboards
python actualizar_todo.py
```
**✨ Características:**
- ✅ **Procesamiento Completo**: Gastos → Reservas → Utilidad → Dashboards
- ✅ **Un solo comando**: Todo el flujo de trabajo automatizado
- ✅ **Manejo de errores**: Continúa o pregunta si falla un paso
- ✅ **Feedback detallado**: Muestra output de cada proceso
- ✅ **Resumen final**: Estadísticas de éxito/fallo

### Opción 1: Ejecutar Todos Simultáneamente (🔥 Recomendado para Visualización)
```bash
# Un solo comando que ejecuta los 5 dashboards
python ejecutar_todos_dashboards.py
```
**✨ Características:**
- ✅ Ejecuta los 5 dashboards automáticamente
- ✅ Un solo terminal necesario
- ✅ Detención fácil con Ctrl+C
- ✅ Verificación automática de archivos
- ✅ URLs mostradas al iniciar

### Opción 2: Ejecutar Todos Manualmente (5 terminales)
```bash
# Terminal 1 - Reservas
python reservas.py

# Terminal 2 - Utilidad Operativa  
python utilidad.py

# Terminal 3 - Marketing
python marketing.py

# Terminal 4 - Gastos de Marketing
python dashboard_gastos_marketing.py

# Terminal 5 - Google Ads
python dashboard_google_ads.py
```

### Opción 3: Ejecutar Individual
```bash
# Solo uno a la vez
python reservas.py                    # Ir a http://localhost:8050
# Ctrl+C para detener
python utilidad.py                    # Ir a http://localhost:8055  
# Ctrl+C para detener
python marketing.py                   # Ir a http://localhost:8056
# Ctrl+C para detener
python dashboard_gastos_marketing.py  # Ir a http://localhost:8057
# Ctrl+C para detener
python dashboard_google_ads.py        # Ir a http://localhost:8058
```

## 🔄 **Flujo de Trabajo Completo**

### **Cuándo usar cada opción:**

#### 🆕 **`actualizar_todo.py`** - Para Actualización Completa
- ✅ **Después de descargar nuevos datos** (bancarios, reservas, marketing)
- ✅ **Configuración inicial** del sistema
- ✅ **Mantenimiento** cuando se actualizan archivos de input
- ✅ **Análisis completo** para obtener insights actualizados

**Orden de ejecución:**
1. 🏦 `gastos_hotboat_sin_drive.py` - Procesar gastos y costos
2. 📅 `Informacion_reservas.py` - Procesar reservas
3. 💰 `estimacion_utilidad_hotboat.py` - Calcular utilidad
4. 📊 `ejecutar_todos_dashboards.py` - Ejecutar dashboards

#### 🔥 **`ejecutar_todos_dashboards.py`** - Para Visualización Rápida
- ✅ **Datos ya procesados** y actualizados
- ✅ **Solo necesitas ver los dashboards**
- ✅ **Análisis rápido** de datos existentes
- ✅ **Presentación** a clientes o equipo

## 🎨 Características de Diseño

### Estilos Visuales:
- **Gradiente Azul:** Header con degradado profesional
- **Efectos Hover:** Botones interactivos con transiciones
- **Estado Activo:** Dashboard actual claramente identificado
- **Iconos:** Emojis para mejorar la experiencia visual

### Responsive Design:
- **Flexbox:** Navegación que se adapta al tamaño de pantalla
- **Gap Spacing:** Espaciado uniforme entre elementos
- **Text Shadow:** Efectos de sombra para mejor legibilidad

## 🔧 Datos y Funcionalidad

### Datos Compartidos:
- Todos los dashboards cargan desde la misma fuente de datos
- Filtros de fecha independientes por dashboard
- Métricas calculadas en tiempo real

### Funcionalidades:
- **Filtros de Fecha:** Rango personalizable en cada dashboard
- **Períodos:** Agrupación por día/semana/mes
- **Gráficos Interactivos:** Plotly con zoom y hover
- **Insights Automáticos:** Conclusiones generadas dinámicamente

## 📱 URLs de Acceso Directo

```
Dashboard de Reservas:        http://localhost:8050
Dashboard de Utilidad:        http://localhost:8055  
Dashboard de Marketing:       http://localhost:8056
Dashboard de Gastos:          http://localhost:8057
Dashboard de Google Ads:      http://localhost:8058
```

## ⚡ Comandos Rápidos

```bash
# 🔄 NUEVO: Actualización completa (procesamiento + dashboards)
python actualizar_todo.py

# 🔥 Ejecutar todos los dashboards (solo visualización)
python ejecutar_todos_dashboards.py

# Ver puertos ocupados
netstat -ano | findstr :805

# Detener todos los procesos Python
taskkill /f /im python.exe

# Alternativa: Ejecutar en 5 terminales separados
python reservas.py & python utilidad.py & python marketing.py & python dashboard_gastos_marketing.py & python dashboard_google_ads.py

# Comandos individuales
python reservas.py                    # Puerto 8050
python utilidad.py                    # Puerto 8055  
python marketing.py                   # Puerto 8056
python dashboard_gastos_marketing.py  # Puerto 8057
python dashboard_google_ads.py        # Puerto 8058
```

## 🔥 Dashboard de Gastos de Marketing - Funcionalidades

### Características Específicas:
- **Comparación Google Ads vs Meta:** Análisis lado a lado de gastos
- **Evolución Temporal:** Gráficos de tendencias por plataforma
- **Distribución por Días:** Análisis de patrones semanales
- **Heatmap de Gastos:** Visualización de gastos por día y mes
- **Insights Automáticos:** Recomendaciones basadas en datos

### Métricas Incluidas:
- 💰 Gasto total por plataforma
- 📊 Gasto promedio diario
- 📱 Conversiones (Google Ads)
- 💡 Costo por conversión
- 📅 Análisis temporal detallado

## 🔥 Dashboard de Google Ads - Nuevas Funcionalidades

### Características Específicas:
- **Series Temporales:** Evolución de métricas por semana
- **Análisis de Campañas:** Rendimiento por campaña
- **Palabras Clave:** Top palabras clave por costo y conversiones
- **Dispositivos:** Distribución de gasto por dispositivo
- **Datos Demográficos:** Análisis por género y edad
- **Día y Hora:** Heatmap de impresiones por día y hora

### Datos Incluidos:
- 📈 Series temporales (13 semanas)
- 🎯 1 campaña activa
- 🔍 13 palabras clave
- 📱 3 tipos de dispositivos
- 👥 Datos demográficos por género y edad
- 📅 Análisis temporal por día y hora

### Preparación de Datos:
```bash
# Extraer archivos del ZIP de Google Ads
python extraer_google_ads.py

# Ejecutar dashboard
python dashboard_google_ads.py
```

---

**✅ Sistema Completamente Funcional**
- ✅ Navegación entre dashboards
- ✅ Estados activos visuales
- ✅ Diseño professional
- ✅ URLs independientes
- ✅ Datos actualizados
- ✅ Nuevo dashboard de gastos
- ✅ Nuevo dashboard de Google Ads 