# 🔄 DIAGRAMA DE FLUJO DE DATOS - HOTBOAT

## 📊 FLUJO PRINCIPAL DE PROCESAMIENTO

```mermaid
graph TD
    A[📁 ARCHIVOS INPUT] --> B[🔄 PROCESAMIENTO]
    B --> C[📊 ARCHIVOS OUTPUT]
    
    subgraph "📁 ARCHIVOS INPUT"
        A1[🏦 Archivos Bancarios]
        A2[📅 Archivos Reservas]
        A3[📈 Archivos Marketing]
        A4[💰 Archivos Costos]
    end
    
    subgraph "🔄 PROCESAMIENTO"
        B1[gastos_hotboat_sin_drive.py]
        B2[Informacion_reservas.py]
        B3[estimacion_utilidad_hotboat.py]
        B4[dashboard_marketing_simple.py]
    end
    
    subgraph "📊 ARCHIVOS OUTPUT"
        C1[gastos hotboat.csv]
        C2[abonos hotboat.csv]
        C3[reservas_HotBoat.csv]
        C4[costos_operativos.csv]
        C5[ingresos_operativos.csv]
        C6[cuenta_corriente_cargos.csv]
        C7[cuenta_corriente_abonos.csv]
    end
```

---

## 🏦 PROCESAMIENTO DE GASTOS Y COSTOS

### 📁 ARCHIVOS INPUT - GASTOS
```
archivos_input/archivos_input_costos/
├── cartola*.xls                    # Cuenta corriente
├── Banco_Estado_*.xlsx            # Chequera Banco Estado
└── Banco_Chile_*.xlsx             # Movimientos Banco Chile
```

### 🔄 CRUCE DE TABLAS - GASTOS

```mermaid
graph LR
    subgraph "🏦 BANCO ESTADO"
        BE1[Fecha]
        BE2[Descripción]
        BE3[Cheques/Cargos]
        BE4[Depósitos/Abonos]
    end
    
    subgraph "🏦 BANCO CHILE"
        BC1[Fecha]
        BC2[Descripción]
        BC3[Monto]
        BC4[Categoría]
        BC5[País]
    end
    
    subgraph "💰 CUENTA CORRIENTE"
        CC1[Fecha]
        CC2[Descripción]
        CC3[Monto]
        CC4[Tipo]
    end
    
    BE1 --> G1[gastos hotboat.csv]
    BE2 --> G1
    BE3 --> G1
    BC1 --> G1
    BC2 --> G1
    BC3 --> G1
    CC1 --> G1
    CC2 --> G1
    CC3 --> G1
    
    BE4 --> G2[abonos hotboat.csv]
    CC3 --> G2
```

### 📊 COLUMNAS DE SALIDA - GASTOS
| Archivo Output | Columnas Principales | Fuente de Datos |
|----------------|---------------------|-----------------|
| `gastos hotboat.csv` | Fecha, Descripción, Monto, Categoría, Categoría_1 | Banco Estado + Banco Chile + Cuenta Corriente |
| `abonos hotboat.csv` | Fecha, Descripción, Monto | Banco Estado + Cuenta Corriente |
| `cuenta_corriente_cargos.csv` | Fecha, Descripción, Monto | Cartola cuenta corriente |
| `cuenta_corriente_abonos.csv` | Fecha, Descripción, Monto | Cartola cuenta corriente |

---

## 📅 PROCESAMIENTO DE RESERVAS

### 📁 ARCHIVOS INPUT - RESERVAS
```
archivos_input/Archivos input reservas/
├── payments_*.csv                  # Pagos
├── appointments_*.csv              # Citas/Reservas
├── reservas_HotBoat.csv           # Reservas existentes
└── HotBoat - Pedidos Extras.csv   # Pedidos adicionales
```

### 🔄 CRUCE DE TABLAS - RESERVAS

```mermaid
graph LR
    subgraph "💳 PAYMENTS"
        P1[ID]
        P2[PAYMENT]
        P3[TOTAL AMOUNT]
        P4[PAID AMOUNT]
        P5[DUE AMOUNT]
        P6[CREATED AT]
    end
    
    subgraph "📅 APPOINTMENTS"
        A1[ID]
        A2[Customer]
        A3[Customer Email]
        A4[SERVICE]
        A5[APPOINTMENT DATE]
        A6[STAFF]
    end
    
    subgraph "📋 RESERVAS EXISTENTES"
        R1[ID]
        R2[fecha_trip]
        R3[Customer Email]
        R4[Service]
    end
    
    P1 --> M1[INNER JOIN on ID]
    A1 --> M1
    
    M1 --> R2[reservas_HotBoat.csv]
    R1 --> R2
```

### 📊 COLUMNAS DE SALIDA - RESERVAS
| Archivo Output | Columnas Principales | Fuente de Datos |
|----------------|---------------------|-----------------|
| `reservas_HotBoat.csv` | ID, fecha_trip, Customer Email, Service, TOTAL AMOUNT, DUE AMOUNT, Customer, STAFF, Phone Number_2 | Payments + Appointments + Reservas existentes |

**Nota:** Las columnas PAID AMOUNT, Phone Number y PAYMENT se eliminan durante el procesamiento. Phone Number_2 se mantiene como número procesado y formateado.

---

## 💰 PROCESAMIENTO DE UTILIDAD

### 🔄 CRUCE DE TABLAS - UTILIDAD

```mermaid
graph LR
    subgraph "📅 RESERVAS"
        R1[ID]
        R2[fecha_trip]
        R3[Customer Email]
        R4[TOTAL AMOUNT]
    end
    
    subgraph "📦 PEDIDOS EXTRA"
        PE1[fecha]
        PE2[email]
        PE3[Total]
    end
    
    subgraph "💰 COSTOS OPERATIVOS"
        CO1[id_reserva]
        CO2[descripción]
        CO3[monto]
    end
    
    R1 --> CO1[costos_operativos.csv]
    R2 --> CO1
    R3 --> CO1
    CO2 --> CO1
    CO3 --> CO1
    
    R2 --> I1[ingresos_operativos.csv]
    R3 --> I1
    R4 --> I1
    PE1 --> I1
    PE2 --> I1
    PE3 --> I1
```

### 📊 COLUMNAS DE SALIDA - UTILIDAD
| Archivo Output | Columnas Principales | Fuente de Datos |
|----------------|---------------------|-----------------|
| `costos_operativos.csv` | fecha, email, id_reserva, descripción, monto | Reservas + Costo fijo por reserva |
| `ingresos_operativos.csv` | fecha, email, id_reserva, descripción, monto | Reservas + Pedidos extra |

---

## 📈 PROCESAMIENTO DE MARKETING

### 📁 ARCHIVOS INPUT - MARKETING
```
archivos_input/archivos input marketing/
├── Comp-1-Conjunto-Anuncios-2Campañas-3-anuncios-por-dia (5).csv    # CON región
├── Comp-1-Conjunto-Anuncios-2Campañas-3-anuncios-por-dia (6).csv    # SIN región
├── gasto diario en google ads.csv
└── gasto diario en meta.csv
```

### 🔄 CRUCE DE TABLAS - MARKETING

```mermaid
graph LR
    subgraph "📊 DATASET CON REGIÓN (5)"
        CR1[Día]
        CR2[Nombre del conjunto de anuncios]
        CR3[Nombre del anuncio]
        CR4[Importe gastado (CLP)]
        CR5[Impresiones]
        CR6[Clics en el enlace]
        CR7[Artículos agregados al carrito]
        CR8[Región]
    end
    
    subgraph "📊 DATASET SIN REGIÓN (6)"
        SR1[Día]
        SR2[Nombre del conjunto de anuncios]
        SR3[Nombre del anuncio]
        SR4[Importe gastado (CLP)]
        SR5[Impresiones]
        SR6[Clics en el enlace]
        SR7[Artículos agregados al carrito]
    end
    
    CR1 --> D1[Dashboard Marketing]
    CR2 --> D1
    CR3 --> D1
    CR4 --> D1
    CR5 --> D1
    CR6 --> D1
    CR7 --> D1
    CR8 --> D1
    
    SR1 --> D1
    SR2 --> D1
    SR3 --> D1
    SR4 --> D1
    SR5 --> D1
    SR6 --> D1
    SR7 --> D1
```

### 📊 COLUMNAS CALCULADAS - MARKETING
| Métrica | Fórmula | Fuente |
|---------|---------|--------|
| CTR | (Clics / Impresiones) × 100 | Dataset (5) y (6) |
| CPC | Importe gastado / Clics | Dataset (5) y (6) |
| Hook Rate 3s | (Reproducciones 3s / Impresiones) × 100 | Dataset (5) y (6) |
| Conversion Rate | (Artículos carrito / Clics) × 100 | Dataset (5) y (6) |
| Cost Per Conversion | Importe gastado / Artículos carrito | Dataset (5) y (6) |

---

## 🔗 FLUJO COMPLETO DE INTEGRACIÓN

```mermaid
graph TD
    subgraph "📁 INPUTS"
        I1[🏦 Archivos Bancarios]
        I2[📅 Archivos Reservas]
        I3[📈 Archivos Marketing]
        I4[💰 Archivos Costos]
    end
    
    subgraph "🔄 PROCESAMIENTO"
        P1[gastos_hotboat_sin_drive.py]
        P2[Informacion_reservas.py]
        P3[estimacion_utilidad_hotboat.py]
        P4[dashboard_marketing_simple.py]
    end
    
    subgraph "📊 OUTPUTS"
        O1[gastos hotboat.csv]
        O2[abonos hotboat.csv]
        O3[reservas_HotBoat.csv]
        O4[costos_operativos.csv]
        O5[ingresos_operativos.csv]
    end
    
    subgraph "📊 DASHBOARDS"
        D1[🌐 Dashboard Reservas - Puerto 8050]
        D2[🌐 Dashboard Utilidad - Puerto 8055]
        D3[🌐 Dashboard Marketing - Puerto 8056]
    end
    
    I1 --> P1
    I2 --> P2
    I3 --> P4
    I4 --> P1
    
    P1 --> O1
    P1 --> O2
    P2 --> O3
    P3 --> O4
    P3 --> O5
    
    O3 --> D1
    O4 --> D2
    O5 --> D2
    O3 --> D2
```

---

## 🎯 CLAVES DE CRUCE PRINCIPALES

| Proceso | Clave de Cruce | Tablas Involucradas |
|---------|----------------|-------------------|
| **Reservas** | `ID` | payments.csv ↔ appointments.csv |
| **Utilidad** | `ID` (reserva) | reservas_HotBoat.csv ↔ costos_operativos.csv |
| **Utilidad** | `email` | reservas_HotBoat.csv ↔ pedidos_extra.csv |
| **Gastos** | `Fecha + Descripción + Monto` | Múltiples archivos bancarios |
| **Marketing** | `Día + Nombre del conjunto de anuncios` | Dataset (5) ↔ Dataset (6) |

---

## 📋 RESUMEN DE ARCHIVOS OUTPUT

| Archivo | Propósito | Columnas Clave |
|---------|-----------|----------------|
| `gastos hotboat.csv` | Gastos consolidados | Fecha, Descripción, Monto, Categoría |
| `abonos hotboat.csv` | Ingresos bancarios | Fecha, Descripción, Monto |
| `reservas_HotBoat.csv` | Reservas procesadas | ID, fecha_trip, Customer Email, Service, TOTAL AMOUNT, DUE AMOUNT, Phone Number_2 |
| `costos_operativos.csv` | Costos por reserva | fecha, email, id_reserva, monto |
| `ingresos_operativos.csv` | Ingresos operativos | fecha, email, id_reserva, monto |
| `cuenta_corriente_*.csv` | Referencia cuenta corriente | Fecha, Descripción, Monto |

---

## 🚀 EJECUCIÓN DEL FLUJO

```bash
# 1. Procesar gastos y costos
python gastos_hotboat_sin_drive.py

# 2. Procesar reservas
python Informacion_reservas.py

# 3. Calcular utilidad
python estimacion_utilidad_hotboat.py

# 4. Ejecutar dashboards
python ejecutar_todos_dashboards.py
```

Este flujo garantiza que todos los datos estén sincronizados y actualizados para los dashboards de análisis. 