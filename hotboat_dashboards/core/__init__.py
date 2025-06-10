#!/usr/bin/env python3
"""
🚤 HOTBOAT - CORE MODULE
========================

Módulo core optimizado para HotBoat Dashboards.
Mantiene la funcionalidad original con mejor organización.
"""

from .data_loader import (
    cargar_datos_reservas,
    cargar_datos_utilidad, 
    cargar_datos_marketing,
    verificar_archivos_datos
)

from .dashboard_styles import (
    get_layout_config,
    get_container_style,
    get_title_style,
    get_card_style,
    get_dropdown_style,
    ESTILOS_ORIGINALES
)

__version__ = "2.0"
__author__ = "Sistema HotBoat Optimizado" 