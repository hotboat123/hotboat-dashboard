# Diccionario de categorías para gastos
# Puedes modificar las palabras clave y categorías según tus necesidades

diccionario_categorias = {
    "Stock_tablas y bebidas": [
        "LIDER.CL"
    ],
    "Ferretería": [
        "FERRETERIA", "SODIMAC", "kupfer", "trapp", "SUPERMERCADO", "sociedad inversione", "full cars", "nutriagro", "unimarc", "mundo pintura", "librer"
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
        "CURSOR", "chatbot"
    ],
    "Compras Internacionales": [
        "aliexpress", "alipays"
    ],
    "Pagos Digitales": [
        "MERCADOPAGO", "MERPAGO", "SumUp", "SUMUP",
    ],
    "Transporte": [
        "UBER", "PAYU *UBER"
    ],
    "Internet": [
        "ENTEL", "STARLINK"
    ],
    "Combustible": [
        "COPEC", "combustible"
    ],
    "Mantención Vehículo": [
        "Diconor", "santa eli"
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
        "aguirre paillale", "Axel Aguirre", "Nestor", 
    ],
    "Sueldo Tom": [
        "Tomas", "Prex"
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
    "Calefonts": [
        "CEM compras"
    ],    
    "Poleras": [
        "77184211"
    ],
    "Gas": [
        "munoz cucha bast", "Javiera Rodriguez"
    ],
    "Mano obra HotBoat daniel": [
        "inostroza canales"
    ],
    "Mano obra HotBoat otros": [
        "Guillermo Ulloa", 
    ],
    
    # Categorías para ABONOS (solo las que te interesan)
    "Bencina Pathfinder": [
        "Odette"
    ],
    "Ingresos HotBoat": [
        "traspaso de:hotboat spa", "Nawrath", "Dutilh"
    ],
    "Aportes de capital": [
        "fintual", "dev Impuesto"
    ]
}


diccionario_categoria_1 = {
    "Costos Fijos": [
        "Arriendo", "Entel", "Bice Vida", "Seguro", "Plan", "Luz", "Electricidad", "Beneficios HotBoat", "Internet" 
    ],
    "Costos Variables": [
        "Gas", "Combustible", "Edicion videos","remuneraciones" # "mantención", "limpieza", "repuestos", "transportes", "comisiones",
    ],
    "Costos de Marketing": [
        "Publicidad Meta", "Publicidad Google", "Herramientas de marketing" # "marketing", "promoción",
    ],
    "Inversión en Activos": [
        "Maquina", "Herramienta", "Inversion", "Flipsky", "Calefonts" # "camara", "dron", "bateria", "motor"
    ],
    "Capital aportado": [
        "Aportes de capital"
    ],
    "Inversión General": [
        "Branding", "Logo", "Sitio web", "Diseño", "Asesoría", "Ferretería", "Compras internacionales", "Mantención Vehículo", "Mano obra HotBoat otros", "Mano obra HotBoat daniel"
    ]
}

descripciones_a_eliminar = [
    "traspaso deuda internacional", "pago pesos tef", "Pedro Antonio", "Cargo por Pago Tc", "Pago Tarjeta de Credito", "TRASPASO DEUDA interna tra.dolar/peso"
] 

costo_operativo_por_reserva = 35000 # Leña, gas, agua, luz, axel(15.000)

# Tabla de correcciones para categorías específicas
# Formato: [fecha, descripcion, monto, categoría_1, categoría_2, observacion]
# Esta tabla permite sobrescribir categorías automáticas y agregar observaciones
# El merge se hace por fecha y monto (sin descripción)
tabla_correcciones = [
    # Ejemplo de corrección:
    ['2025-07-17', 'Traspaso A:Daniel Inostroza Canales', 1000000, 'Inversión en Activos', 'HotBoat matriz', 'Pago a daniel para hacer matriz'],
    ['2025-07-04','','500000','Inversión en Activos','HotBoat matriz','Pago a daniel para hacer matriz'],
    ['2025-07-14','','437135','Inversión General','Mantención','Pintura Marathon 550'],
    ['2025-07-01','','302310','Inversión en Activos','HotBoat 1','Caldera inox, mano de obra'],
    ['2025-07-21','','200000','Inversión en Activos','Herramienta','Bajada Lancha'],
    ['2025-07-07','','179000','Inversión en Activos','Balones de gas','Balon de gas'],
    ['2025-07-07','','173847','Inversión en Activos','Dispositivos','Llaves de paso y temperatura'],
    ['2025-07-05','','150613','Inversión en Activos','Bombas','Bombas seaflo'],
    ['2025-07-16','','119609','Inversión en Activos','Infraestructura','Materiales invernadero'],
    ['2025-07-14','','118500','Inversión General','Mantención','mano de obra'],
    ['2025-07-07','','110000','Inversión General','mantención','mano de obra'],
    ['2025-07-14','','93500','Inversión General','Mantención','mano de obra'],
    ['2025-07-07','','100000','Inversión en Activos','sistema calentamiento','aislamiento'],
    ['2025-07-07','','70000','Inversión en Activos','HotBoat 2','Leñera HB2'],
    # [''2025-02-10', 'SODIMAC compra herramientas', 25000, 'Ferretería', 'Inversión General', 'Herramientas para mantención''],
]

# Diccionario de categorías para cuenta corriente
# Categorías específicas para los movimientos de cuenta corriente

