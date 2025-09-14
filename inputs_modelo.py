# Diccionario de categorías para gastos
# Puedes modificar las palabras clave y categorías según tus necesidades

diccionario_categorias_gastos = {
    "Stock tablas y bebidas": [
        "LIDER.CL"
    ],
    "leña": [
        "Jaime Catricheo"
    ],
    "Ferretería": [
        "FERRETERIA", "SODIMAC", "kupfer", "trapp", "SUPERMERCADO", "sociedad inversione", "full cars", "nutriagro", "unimarc", "librer", "doble rr"
    ],
    "Publicidad Meta": [
        "FACEBK", "facebook"
    ],
    "Publicidad Google": [
        "google", "facebook"
    ],
    "Sitio Web": [
        "hostinger", "facebook"
    ],
    "Herramientas de marketing": [
        "CURSOR", "chatbot", "safe traveler"
    ],
    "Compras Internacionales": [
        "aliexpress", "alipays"
    ],
    "Transporte": [
        "UBER", "PAYU *UBER"
    ],
    "Internet": [
        "ENTEL", "STARLINK"
    ],
    "Combustible": [
        "COPEC", "combustible", "SHELL"
    ],
    "Mantención Vehículo": [
        "Diconor", "santa eli"
    ],
    "Mantención HotBoat": [
        "mundo pintura",
    ],
    "edicion videos": [
        "Fiverr"
    ],
    "Alimentos": [
        "FAMILIA UNIDA", "AFUNAYUN"
    ],
    "Seguros": [
        "BICE VIDA", "cargo seguro proteccion bancaria"
    ],
    "Importaciones": [
        "IMPORTADORA"
    ],
    "Otros": [
        "CANVA", "LIBRERIA", "VIATOR"
    ],
    "Remuneraciones": [
        "aguirre paillale", "Axel Aguirre", "Nestor", "Francisco godoy"
    ],
    "Sueldo Tom": [
        "Tomas Andreas", "Prex"
    ],
    "Beneficios HotBoat": [
        "Felipe Hidalgo", 
    ],
    "Arriendo": [
        "quiroga toro"
    ],
    "Motores HotBoat": [
        "flipsky"
    ],
    "Drones": [
        "ebest"
    ],
    "Calefonts": [
        "CEM compras", "CEM SANTIAGO"
    ],    
    "Poleras": [
        "77184211"
    ],
    "Gas": [
        "munoz cucha bast", "Javiera Rodriguez", "ferrete las condes", "ferr cl", "ferrete com", "mercadopagoferreteria"
    ],
    "Mano obra HotBoat daniel": [
        "inostroza canales"
    ],
    "Mano obra HotBoat otros": [
        "Guillermo Ulloa"
    ],
    "Intereses": [
        "Pago automatico tarjeta de credito", "amortizacion linea de credito" 
    ],
}


# Diccionario de categorías 1 para GASTOS
diccionario_categoria_1_gastos = {
    "Costos Fijos": [
        "Arriendo", "Entel", "Bice Vida", "Seguro", "Plan", "Luz", "Electricidad", "Beneficios HotBoat", "Internet", 
    ],
    "Costos Variables": [
        "Gas", "Combustible", "Edicion videos","remuneraciones", "leña", "Stock tablas y bebidas" # "mantención", "limpieza", "repuestos", "transportes", "comisiones",
    ],
    "Costos de Marketing": [
        "Publicidad Meta", "Publicidad Google", "Herramientas de marketing" # "marketing", "promoción",
    ],
    "Inversión en Activos": [
        "Herramientas", "Calefonts", "Poleras", "Motores HotBoat", "Infraestructura" , "Estanques", "camara", "Drones", "bateria", "Antena starlink"
    ],
    "Capital aportado": [
        "Aportes de capital"
    ],
    "Inversión General": [
        "Branding", "Logo", "Sitio web", "Diseño", "Asesoría", "Ferretería", "Compras internacionales", "Mantención Vehículo", "Mano obra HotBoat otros", "Mano obra HotBoat daniel", "Intereses", "Mantención HotBoat"
    ],
    "Sueldo Tom": [
        "Sueldo Tom"
    ],
}

# Deudas manuales por compras en cuotas (input explícito)
# Formato por fila:
# [fecha_compra, descripcion, monto_de_la_cuota, numero_cuotas, categoria_1, categoria_2, observacion]
# La deuda agregada será: Monto = monto_de_la_cuota * numero_cuotas; Origen='deudas'
deudas_manual = [
    # Ejemplo:
    # ['2025-08-16', 'Compresor ABC', 538746, 1, 'Inversión en Activos', 'Compresor', 'Deuda manual compresor'],
    ['2025-08-16', 'Mercado', 46082, 12, 'Inversión en Activos', 'Drones', 'Dron 2'],
]

descripciones_a_eliminar_gastos = [ #tien e que ser exacto
    "traspaso deuda internacional", "pago pesos tef", "Pedro Antonio", "Cargo por Pago Tc", "Pago Tarjeta de Credito", "TRASPASO DEUDA interna tra.dolar/peso", "tef a damjanic silva tomas andreas", "Traspaso a:Hotboat Spa", "HotBoat compras", "traspaso a:tomas ramirez rondon", "Amortizacion linea de credito", "JUNCALILLO", "Amortizacion A Linea De Credito",
"pago linea de credito", "Traspaso De:Tomas Damja", "flybondi", "jetsmar", "uber", "santos", "busbud"
] 

# Lista de registros específicos a eliminar por fecha y monto
# Formato: [fecha, monto]
# La fecha puede ser en formato 'YYYY-MM-DD' o 'DD/MM/YYYY'
eliminaciones_fecha_monto_gastos = [
    # Ejemplo de eliminaciones:
    ['2025-04-21', 1400000],  
    ['2025-04-21', 1400000],  
    ['2025-05-30', 35660],    
    ['2025-05-27', 32220],
    ['2025-05-14', 275395.5],  #devolucion sobre abono (al parecer era excedente de dolares que se transfirio a mi cuenta corriente en dolares)

    # ['15/07/2025', 25000],    # Eliminar registro del 15 de julio 2025 por $25,000
    # ['2025-06-01', 100000],   # Eliminar registro del 1 de junio 2025 por $100,000
] 

# Lista de registros a eliminar por fecha y descripción (contains)
# Formato: [fecha, texto_en_descripcion]
# La fecha puede ser 'YYYY-MM-DD' o 'DD/MM/YYYY'. La descripción hace match por contains insensible a mayúsculas.
eliminaciones_fecha_descripcion_gastos = [
    # Ejemplos:
    ['2025-06-19', 'falabella'],
    ['2025-06-13', 'JETSMAR'],
    ['2025-08-12', 'sky'],
    ['2025-08-09', 'rushersky'],
    ['2025-08-28', 'airbnb'],
    ['2025-08-18', 'fintoc'],
    ['2025-08-27', 'rock'],
    # ['15/07/2025', 'spa santiago'],
]

costo_operativo_por_reserva = 35000 # Leña, gas, agua, luz, axel(15.000)

# Valor aproximado del dólar para conversiones de USD a CLP
valor_aproximado_dolar = float(950)  # Actualizar según tipo de cambio actual

# Tabla de correcciones para categorías específicas
# Formato: [fecha, descripcion, monto, categoría_1, categoría_2, observacion]
# Esta tabla permite sobrescribir categorías automáticas y agregar observaciones
# El merge se hace por fecha y monto (sin descripción)
tabla_correcciones_gastos = [
    # Ejemplo de corrección:
    ['2025-07-17', 'Traspaso A:Daniel Inostroza Canales', 1000000, 'Inversión en Activos', 'HotBoat matriz', 'Pago a daniel para hacer matriz'],
    ['2025-07-04','','500000','Inversión en Activos','HotBoat matriz','Pago a daniel para hacer matriz'],
    ['2025-07-14','','437135','Inversión General','Mantención','Pintura Marathon 550'],
    ['2025-07-01','','302310','Inversión en Activos','HotBoat 1','Caldera inox, mano de obra'],
    ['2025-07-21','','200000','Inversión en Activos','Infraestructura','Bajada Lancha'],
    ['2025-07-07','','179000','Inversión en Activos','Balones de gas','Balon de gas'],
    ['2025-05-26','','184000','Inversión en Activos','Balones de gas','Balon de gas'],
    ['2025-07-07','','173847','Inversión en Activos','Dispositivos','Llaves de paso y temperatura'],
    ['2025-07-05','','150613','Inversión en Activos','Bombas','Bombas seaflo'],
    ['2025-07-16','','119609','Inversión en Activos','Infraestructura','Materiales invernadero'],
    ['2025-07-14','','118500','Inversión General','Mantención','mano de obra'],
    ['2025-07-07','','110000','Inversión General','mantención','mano de obra'],
    ['2025-07-14','','93500','Inversión General','Mantención','mano de obra'],
    ['2025-07-07','','100000','Inversión en Activos','sistema calentamiento','aislamiento'],
    ['2025-07-07','','70000','Costos Variables','Remuneraciones','pago nestor(algo caballo)'],
    ['2025-06-27','','27500','Inversión en Activos','HotBoat 2','Leñera HB2'],
    ['2025-02-25','','283033.5','Costos de Marketing','Externalizacion Marketing','Pago a Arbi'],
    ['2025-02-10','','365265','Inversión en Activos','Calefonts','Calefont 2'],
    ['2025-03-20','','198623','Devolucion a cliente','Devolucion a cliente','Devolucion a cliente'],
    ['2025-08-17','','97475','Devolucion a cliente','Devolucion a cliente','Devolucion a cliente'],
    ['2025-04-08','','190000','Inversión en Activos','Infraestructura' ,'Bajada Lancha'],
    ['2025-01-22','','177705','Inversión en Activos','Herramientas' ,'Lija Orbital'],
    ['2025-01-13','','157204','Inversión en Activos','Estanques' ,'Estanque 1400L'],
    ['2025-01-30','','144282','Inversión en Activos','Materiales HotBoat 3' ,'Monomero Estireno'],
    ['2025-01-12','','116991','Inversión en Activos','Drones' ,'Dron'],
    ['2025-05-28','','173300','Inversión en Activos','Antena starlink' ,'Antena starlink'],
    ['2025-05-30','','9800','Inversión en Activos','Herramientas' ,'Llave Inglesa'],
    ['2025-05-30','','51780','Inversión en Activos','Calefonts' ,'Aislante mangueras y flotadores bomba'],
    ['2025-05-30','','47123','Inversión en Activos','HotBoat 3' ,'Reductor 48V a 12V'],
    ['2025-05-30','','68125','Inversión en Activos','HotBoat 3' ,'Cableado HotBoat 3'],
    ['2025-05-29','','128647','Inversión en Activos','Sistema inteligente' ,'Inversor 48V a 220V'],
    ['2025-05-29','','23646','Inversión en Activos','Sistema Inteligente' ,'Interruptor Automático'],
    ['2025-05-26','','13423','Inversión en Activos','Herramientas' ,'Medidor de Humedad'],
    ['2025-05-26','','22758','Inversión en Activos','Sistema inteligente' ,'Sensor de gas y linterna frontal'],
    ['2025-07-30','','30000','Costos Variables','Leña' ,'Leña juan otarola'],
    ['2025-07-28','','40000','Costos Variables','Devolucion clientes' ,'Devolucion a cliente'],
    ['2025-08-08','','65000','Inversión en Activos','HotBoat matriz' ,'Fierros y ruedas matriz exterior'],
    ['2025-08-04','','177600','Inversión en Activos','HotBoat matriz' ,'Terciados matriz exterior'],
    ['2025-08-01','','27500','Inversión en Activos','HotBoat 2' ,'2da mitad leñera'],
    ['2025-08-15','','17999','Inversión en Activos','Iluminacion Laguna' ,'Alargador 20 metros'],
    ['2025-08-13','','16691','Inversión en Activos','Sistema inteligente' ,'Fuente de poder'],
    ['2025-08-19','','66851','Inversión en Activos','HotBoat 1' ,'Sistema Iluminacion: botones inox y caja ip67 botones'],
    ['2025-08-22','','17661','Inversión en Activos','HotBoat 1' ,'Sistema Iluminacion: caja ip67 fusibles'],
    ['2025-08-16','','552990','Inversión en Activos','Drones' ,'Dron 2'],
    ['2025-08-16','','538746','Inversión en Activos','Compresor' ,'Compresor'],


    # [''2025-02-10', 'SODIMAC compra herramientas', 25000, 'Ferretería', 'Inversión General', 'Herramientas para mantención''],
]

# Lista de gastos pagados en efectivo
# Formato: [fecha, descripcion, monto, categoria_1, categoria_2, observacion]
# Estos gastos se agregarán con origen 'Efectivo'
gastos_efectivo_gastos = [
    # Ejemplos de gastos en efectivo:
    ['2025-07-30','Compra leña en efectivo juan otarola','30000','Costos Variables','Leña' ,'Leña juan otarola'],
    ['2025-08-08','Compra leña en efectivo verduleria','7000','Costos Variables','Leña' ,'Leña verduleria'],
    ['2025-08-12','Compra leña en efectivo verduleria','45000','Costos Variables','Leña' ,'Leña juan otarola'],
    ['2025-08-15','Compra leña en efectivo verduleria','45000','Costos Variables','Remuneraciones' ,'Pago nestor'],
    # ['2025-01-15', 'Compra herramientas ferretería local', 25000, 'Inversión General', 'Ferretería', 'Compra en efectivo'],
    # ['2025-01-20', 'Combustible gasolina', 30000, 'Costos Variables', 'Combustible', 'Pago en efectivo estación servicio'],
    # ['2025-01-25', 'Almuerzo equipo trabajo', 15000, 'Costos Variables', 'Alimentos', 'Almuerzo pagado en efectivo'],
]

############################
# ABONOS - CONFIGURACIÓN   #
############################

# Diccionario de categorías 1 para ABONOS
# Reglas solicitadas: Inversión, Ingreso operativo, otros (según Categoría_2)
diccionario_categoria_1_abonos = {
    'Inversión': [
        'aportes de capital'
    ],
    'Ingreso operativo': [
        'ingreso transbank diario', 'ingreso mercadopago diario', 'ingreso hotboat', "ingreso transferencia hotboat diario"
    ],
    'otros': [
        'otros'
    ],
}

# Opcional: Diccionario de categorías 2 para ABONOS (si se quisiera forzar por keywords)
diccionario_categorias_abonos = {
    'aportes de capital': ["fintual", "dev Impuesto"],
    'ingreso transbank diario': ['transbank', 'tbk'],
    'ingreso mercadopago diario': ['mercado pago', 'mercadopago', 'mpago'],
    'ingreso transferencia hotboat diario': ['TEF', "DEPOSITO EN EFECTIVO"],
    'ingreso hotboat': ["Traspaso De:Hotboat Spa", "Nawrath", "Dutilh", "alberto eduardo", "rodrigo fredes", "patricio eduardo", "tomas damjanic"],
    'otros': ['Odette']
}


# Filtros/limpiezas específicos de ABONOS
descripciones_a_eliminar_abonos = [
    # ejemplos:
    "traspaso deuda internacional", "pago pesos tef", "Pedro Antonio", "fani yutronic" , "sacha", "Giuseppe", "Transferencia Desde Linea De Credito", "Pago:proveedores 0762966190", "dinko damjanic", "tomas andreas", "dominique denise", "lucas andres"
]

eliminaciones_fecha_monto_abonos = [
    # ['2025-07-15', 50000],
    ['2025-04-16', 1400000], 
    ['2025-08-09', 50000], 
]

eliminaciones_fecha_descripcion_abonos = [
    # ['2025-07-15', 'texto en descripcion'],
]

# Correcciones para ABONOS (merge por Fecha+Monto)
# Formato: [fecha, descripcion, monto, categoría_1, categoría_2, observacion]
tabla_correcciones_abonos = [
    # ['2025-07-20', '', 150000, 'Ingreso operativo', 'ingreso transbank', 'Ajuste manual'],
]

# Ingresos en efectivo a sumar a los abonos
# Formato: [fecha, descripcion, monto, categoria_1, categoria_2, observacion]
ingresos_efectivo_abonos = [
    # ['2025-07-30', 'Ingreso caja chica', 50000, 'Ingreso operativo', 'otros', 'Ingreso manual'],
]

# Diccionario de categorías para cuenta corriente
# Categorías específicas para los movimientos de cuenta corriente

############################
# CONFIG ÚNICO             #
############################

# Diccionario único de configuración para el procesamiento
config_procesamiento = {
    'global': {
        'valor_aproximado_dolar': valor_aproximado_dolar,
        'año_para_fecha_banco_estado': '2025',
    },
    'gastos': {
        'diccionario_categorias': diccionario_categorias_gastos,
        'diccionario_categoria_1': diccionario_categoria_1_gastos,
        'deudas_manual': deudas_manual,
        'descripciones_a_eliminar': descripciones_a_eliminar_gastos,
        'eliminaciones_fecha_monto': eliminaciones_fecha_monto_gastos,
        'eliminaciones_fecha_descripcion': eliminaciones_fecha_descripcion_gastos,
        'tabla_correcciones': tabla_correcciones_gastos,
        'gastos_efectivo': gastos_efectivo_gastos,
    },
    'abonos': {
        'diccionario_categorias': diccionario_categorias_abonos,
        'diccionario_categoria_1': diccionario_categoria_1_abonos,
        'descripciones_a_eliminar': descripciones_a_eliminar_abonos,
        'eliminaciones_fecha_monto': eliminaciones_fecha_monto_abonos,
        'eliminaciones_fecha_descripcion': eliminaciones_fecha_descripcion_abonos,
        'tabla_correcciones': tabla_correcciones_abonos,
        'ingresos_efectivo': ingresos_efectivo_abonos,
    }
}

# Configuración para Utilidad Operativa
# Permite activar/desactivar ajustes específicos de la consolidación
config_utilidad_operativa = {
    # Si True, en costos fijos se considera monto=0 cuando la descripción contiene "Sueldo Tom"
    'ignorar_sueldo_tom_en_costos_fijos': True,
    # Desglose por producto para costos operativos (valores relativos; se escalan al monto por reserva)
    # Claves: nombre de producto (como en columna Service sin el precio) o 'default'
    # Ejemplo de claves de producto: 'HotBoat Trip 2 people', 'HotBoat Trip 3 people', etc.
    'costo_operativo_detalle_por_producto': {
        'default': {
            'Gas': 10000,
            'Leña': 1500,
            'Agua': 700,
            'Luz': 520,
        }

        # Puedes definir productos específicos si requieren proporciones distintas, por ejemplo:
        # 'HotBoat Trip 2 people': {
        #     'Gas': 12000,
        #     'Leña': 14000,
        #     'Agua': 800,
        #     'Luz': 600,
        # }
    },
    # Si True, el desglose anterior se escala exactamente al 'monto' de cada reserva
    'ajustar_costos_operativos_a_monto_por_reserva': False,
}

### notas
# nose en que fecha, pero antes, me deposite 50 de chile a prex desde bco de chile en vez de bco estado, entonces luego transferi los 50 desde estado a chile
# 11 septiembre compre super con banco estado en vez de prex
# 12 de septiembre se transfire 160650 desde estado a chile para pagar gelcoat
# 12 de septiembre compre 7200 con prex en vez e bco estado pq no tenia la billetera, era bolsas de basura y palmito en lata
