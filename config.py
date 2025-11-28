# =============================================================================
# config.py
# Archivo centralizado para todas las constantes globales de configuración.
# Estas variables definen las dimensiones de pantalla, velocidad del juego
# y colores comunes para el renderizado.
# =============================================================================

# -----------------------------------------------------------------------------
#region DIMENSIONES DE LA VENTANA
# -----------------------------------------------------------------------------
# Resolución base del juego.  
# Se recomienda mantenerla fija porque muchos elementos del nivel dependen
# de posiciones absolutas y tiles gráficos predefinidos.
ANCHO = 800
ALTO = 600
# endregion
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
#region RENDIMIENTO Y FRAMERATE
# -----------------------------------------------------------------------------
# FPS objetivo del juego. Afecta:
# - velocidad del bucle principal
# - estabilidad del movimiento y animaciones
# - rendimiento general
FPS = 60
# endregion
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
#region COLORES GLOBALes
# -----------------------------------------------------------------------------
# Color de fondo usado cuando no se carga un background específico.
# El color se aplica como fallback en BaseLevel._draw_background()
COLOR_FONDO = (18, 18, 30)
# endregion
# -----------------------------------------------------------------------------
