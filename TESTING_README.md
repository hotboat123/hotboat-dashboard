# 🧪 Sistema de Testing HotBoat Dashboard

## 📖 ¿Qué son los Tests de Regresión?

Los **tests de regresión** son una práctica fundamental en desarrollo de software que asegura que los cambios nuevos no rompan funcionalidad existente. En nuestro contexto de dashboards, estos tests:

- ✅ **Validan** que los datos se carguen correctamente
- ✅ **Verifican** que las métricas calculadas sean consistentes  
- ✅ **Detectan** cambios inesperados en resultados
- ✅ **Protegen** contra errores introducidos por modificaciones

## 🏗️ Estructura del Sistema de Testing

```
tests/
├── __init__.py                    # Convierte carpeta en paquete Python
├── test_data_loading.py           # Tests de carga de datos
├── test_dashboard_outputs.py      # Tests de creación de dashboards
├── test_metricas_regression.py    # Tests de regresión de métricas
├── run_all_tests.py              # Script para ejecutar todos los tests
├── snapshots/                    # Snapshots de datos para comparación
│   └── data_snapshot.json
└── baselines/                    # Métricas baseline para regresión
    └── metricas_baseline.json
```

## 🎯 Tipos de Tests Implementados

### 1. **Tests de Carga de Datos** (`test_data_loading.py`)
- Verifica que `cargar_datos()` funcione sin errores
- Valida estructura y formato de los DataFrames
- Detecta archivos faltantes o corruptos
- Revisa calidad básica de datos

### 2. **Tests de Dashboard Outputs** (`test_dashboard_outputs.py`)  
- Confirma que las apps de Dash se creen correctamente
- Valida que los layouts estén configurados
- Guarda snapshots para comparación futura
- Detecta cambios en estructura de datos

### 3. **Tests de Regresión de Métricas** (`test_metricas_regression.py`)
- Calcula métricas clave del sistema
- Compara con valores baseline establecidos
- Alerta sobre cambios significativos (>1% por defecto)
- Mantiene historial de métricas

## 🚀 Cómo Usar el Sistema

### Instalación de Dependencias
```bash
pip install -r requirements-testing.txt
```

### Ejecutar Todos los Tests
```bash
python tests/run_all_tests.py
```

### Ejecutar Tests Individuales
```bash
# Tests de carga de datos
python tests/test_data_loading.py

# Tests de dashboard outputs  
python tests/test_dashboard_outputs.py

# Tests de regresión de métricas
python tests/test_metricas_regression.py
```

### Usar con pytest (Avanzado)
```bash
# Ejecutar todos los tests con pytest
pytest tests/ -v

# Con reporte de coverage
pytest tests/ --cov=dashboards --cov-report=html

# Generar reporte HTML
pytest tests/ --html=report.html --self-contained-html
```

## 📊 Interpretando los Resultados

### ✅ **Tests Exitosos**
```
✅ cargar_datos() ejecutado exitosamente
✅ Estructura de datos validada correctamente
✅ App de reservas creada exitosamente
✅ total_ingresos: Sin cambios significativos (0.05%)
```

### ⚠️ **Advertencias**
```
⚠️ Columna 'precio_total' no encontrada en reservas
⚠️ Cambio detectado en 'total_ingresos':
   Anterior: 150,000.00
   Actual: 155,000.00  
   Diferencia: 3.33% (tolerancia: 1.0%)
```

### ❌ **Errores**
```
❌ TEST FALLÓ: cargar_datos() falló: [Errno 2] No such file or directory
❌ Error al crear app de reservas: ImportError: cannot import name...
```

## 🔧 Configuración y Personalización

### Ajustar Tolerancia de Regresión
En `test_metricas_regression.py`, línea 28:
```python
cls.tolerance = 0.01  # 1% - Cambiar según necesidades
```

### Agregar Nuevas Métricas
En `calcular_metricas_clave()`, agregar:
```python
# Tu nueva métrica
if 'nueva_columna' in df.columns:
    metricas['nueva_metrica'] = float(df['nueva_columna'].sum())
```

### Crear Baseline Inicial
Después de confirmar que los datos están correctos:
```bash
python tests/test_metricas_regression.py
```
Esto creará `tests/baselines/metricas_baseline.json`

## 🔄 Flujo de Trabajo Recomendado

### 1. **Antes de Hacer Cambios**
```bash
# Ejecutar tests para establecer estado actual
python tests/run_all_tests.py
```

### 2. **Después de Hacer Cambios**
```bash
# Verificar que no se rompió nada
python tests/run_all_tests.py
```

### 3. **Si hay Cambios Esperados en Métricas**
```bash
# Actualizar baseline después de validar cambios
python tests/test_metricas_regression.py
```

### 4. **Antes de Commit/Deploy**
```bash
# Validación final
python tests/run_all_tests.py
```

## 📈 Beneficios del Sistema

### 🛡️ **Protección contra Errores**
- Detecta automáticamente cuando algo se rompe
- Previene deploy de código defectuoso
- Mantiene calidad consistente

### 📊 **Monitoreo de Datos**
- Alerta sobre cambios inesperados en métricas
- Valida integridad de datos de entrada
- Detecta problemas de calidad de datos

### 🚀 **Confianza en Desarrollo** 
- Permite refactorizar código con seguridad
- Facilita agregar nuevas funcionalidades
- Reduce tiempo de debugging

### 📝 **Documentación Automática**
- Los tests sirven como documentación viva
- Muestran cómo debe comportarse el sistema
- Registran expectativas sobre datos

## 🔧 Troubleshooting

### Problema: "ImportError: cannot import name"
**Solución:** Verificar que estés en el directorio correcto:
```bash
cd /path/to/hotboat/project
python tests/run_all_tests.py
```

### Problema: "No such file or directory"
**Solución:** Verificar que los archivos de datos estén en las rutas correctas.

### Problema: Tests fallan después de cambios de datos
**Solución:** Si los cambios son esperados, actualizar baseline:
```bash
python tests/test_metricas_regression.py
```

## 🎯 Próximos Pasos

1. **Ejecutar tests regularmente** - Especialmente antes de commits
2. **Expandir cobertura** - Agregar tests para funciones específicas
3. **Automatizar** - Integrar con Git hooks o CI/CD
4. **Monitorear** - Revisar trends en métricas a lo largo del tiempo

---

## 📞 Soporte

Si tienes problemas con los tests:
1. Revisa los logs detallados arriba de cada error
2. Verifica que las dependencias estén instaladas
3. Asegúrate de ejecutar desde el directorio correcto
4. Consulta este README para configuración

**¡El sistema de testing es tu aliado para mantener dashboards confiables! 🚤✨** 