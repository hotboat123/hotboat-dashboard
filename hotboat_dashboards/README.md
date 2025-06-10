# 🚤 HOTBOAT DASHBOARDS OPTIMIZADO

**Versión 2.0 - Optimizada y Funcional**

Sistema de dashboards optimizado que mantiene la **funcionalidad exacta** de la versión original, pero con una estructura más limpia y ordenada.

## ✨ Características

- **🎨 Interfaz Original**: Mantiene la interfaz negra con selector arriba que funciona
- **📂 Estructura Modular**: Código organizado en módulos core y dashboards
- **🔧 Funcionalidad Exacta**: Misma funcionalidad de la versión original que trabaja
- **🚀 Ejecución Simple**: Comando unificado para ejecutar dashboards
- **📊 3 Dashboards**: Reservas, Utilidad y Marketing en puertos específicos

## 📁 Estructura Optimizada

```
hotboat_dashboards/
├── core/                          # Módulos centrales optimizados
│   ├── __init__.py               # Inicialización del paquete
│   ├── data_loader.py            # Cargador de datos centralizado
│   └── dashboard_styles.py       # Estilos originales que funcionan
├── dashboards/                    # Dashboards individuales
│   └── reservas_dashboard.py     # Dashboard de reservas optimizado
├── run_dashboards.py             # Launcher principal optimizado
└── README.md                     # Esta documentación
```

## 🚀 Uso Rápido

### Ejecutar Dashboards Individuales

```bash
# Dashboard de Reservas (puerto 8050)
python hotboat_dashboards/run_dashboards.py reservas

# Dashboard de Utilidad (puerto 8055)  
python hotboat_dashboards/run_dashboards.py utilidad

# Dashboard de Marketing (puerto 8056)
python hotboat_dashboards/run_dashboards.py marketing
```

### Ejecutar Todos los Dashboards

```bash
# Ejecuta los 3 dashboards simultáneamente
python hotboat_dashboards/run_dashboards.py todos
```

### Ayuda

```bash
python hotboat_dashboards/run_dashboards.py help
```

## 🌐 URLs de Acceso

Una vez ejecutados, los dashboards están disponibles en:

- **📊 Reservas**: http://localhost:8050
- **💰 Utilidad**: http://localhost:8055  
- **📱 Marketing**: http://localhost:8056

## 🔧 Módulos Core

### `data_loader.py`
Centraliza la carga de datos para todos los dashboards:
- `cargar_datos_reservas()`: Para dashboard de reservas
- `cargar_datos_utilidad()`: Para dashboard de utilidad
- `cargar_datos_marketing()`: Para dashboard de marketing
- `verificar_archivos_datos()`: Validación de archivos

### `dashboard_styles.py`
Mantiene los estilos originales que funcionan:
- Interfaz negra con selector arriba
- Estilos de tarjetas y gráficos
- Configuración de layout original

## 📊 Dashboards

### Dashboard de Reservas
- **Puerto**: 8050
- **Funcionalidad**: Análisis de reservas y finanzas
- **Características**: Mismo layout y funciones de la versión original

### Dashboard de Utilidad  
- **Puerto**: 8055
- **Funcionalidad**: Análisis de utilidad operativa
- **Características**: Gráficos interactivos y métricas financieras

### Dashboard de Marketing
- **Puerto**: 8056
- **Funcionalidad**: Análisis de campañas y métricas de marketing
- **Características**: Análisis de CPC, CTR y conversiones

## ⚡ Ventajas de la Versión Optimizada

1. **🧹 Código Más Limpio**: Funciones comunes centralizadas
2. **📂 Mejor Organización**: Estructura modular clara
3. **🔧 Fácil Mantenimiento**: Cambios centralizados en core
4. **🚀 Ejecución Simplificada**: Un solo comando para todo
5. **📊 Mismo Rendimiento**: Funcionalidad exacta de la original
6. **🎨 Interfaz Intacta**: Mantiene el look que funciona

## 🔄 Compatibilidad

- **✅ Datos**: Usa los mismos archivos de `archivos_output/`
- **✅ Funciones**: Mantiene todas las funciones originales de `funciones/`
- **✅ Interfaz**: Interfaz negra original que funciona
- **✅ Puertos**: Mismos puertos (8050, 8055, 8056)

## 📋 Dependencias

El sistema optimizado mantiene las mismas dependencias:
- `dash`
- `pandas` 
- `plotly`
- `datetime`

## 🛠️ Instalación

1. **Verificar estructura**: Los archivos originales deben estar en la raíz
2. **Ejecutar optimizado**: Usar los comandos del launcher
3. **Acceder dashboards**: En las URLs especificadas

## 💡 Filosofía de Optimización

> **"Si funciona, no lo rompas. Sólo hazlo más ordenado."**

Esta versión optimizada:
- ✅ **Mantiene** toda la funcionalidad original
- ✅ **Conserva** la interfaz que funciona  
- ✅ **Mejora** la organización del código
- ✅ **Simplifica** la ejecución
- ❌ **NO cambia** la lógica de negocio
- ❌ **NO modifica** los estilos funcionales

## 🔗 Comandos de Backup

Si necesitas volver a la versión original, simplemente usa:
```bash
python dashboards.py      # Dashboard original de reservas
python utilidad.py        # Dashboard original de utilidad  
python marketing.py       # Dashboard original de marketing
```

---

**🚤 HotBoat Dashboards v2.0** - Optimizado, ordenado y funcional. 