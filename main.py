# =============================================================================
# main.py
# Punto de entrada del juego Super Pang en Python.
# Inicializa Pygame, crea el nivel actual, ejecuta el loop principal
# y gestiona la actualización/render del juego.
# =============================================================================

import pygame
from config import ANCHO, ALTO, FPS
from core.level.level1 import Level1


# =============================================================================
#region MAIN LOOP
# =============================================================================
def main():
    # -------------------------------------------------------------------------
    # Inicialización del motor Pygame
    # -------------------------------------------------------------------------
    pygame.init()
    pygame.mixer.init()  # Sonido y música

    # Crear ventana principal
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    reloj = pygame.time.Clock()

    # -------------------------------------------------------------------------
    # Inicializar el Nivel
    # -------------------------------------------------------------------------
    # Cada nivel hereda de BaseLevel, por lo que mantiene estructura estándar.
    lvl = Level1(pantalla, ANCHO, ALTO)

    # Cargar imágenes, tiles, plataformas, HUD, jugador, etc.
    lvl.load_assets()

    # Crear bolas iniciales especificadas por el nivel
    lvl.spawn_initial_entities()

    # -------------------------------------------------------------------------
    # Loop principal del juego
    # -------------------------------------------------------------------------
    corriendo = True
    while corriendo:

        # Tiempo por cuadro (frame time)
        dt = reloj.tick(FPS)

        # Leer eventos
        eventos = pygame.event.get()
        for evento in eventos:
            if evento.type == pygame.QUIT:
                corriendo = False

        # Manejo de input (movimiento, disparos, reinicio, salir)
        should_continue = lvl.handle_events(eventos)
        if not should_continue:
            corriendo = False

        # Actualización general del nivel:
        # jugador, balas, bolas, plataformas, colisiones, timer, estado WIN/LOSS.
        lvl.update(dt)

        # Renderizado completo: fondo, límites, entidades, HUD
        lvl.draw()

        # Actualizar pantalla
        pygame.display.flip()

    # -------------------------------------------------------------------------
    # Cleanup al salir
    # -------------------------------------------------------------------------
    lvl.detener_musica()
    pygame.quit()
# endregion
# =============================================================================


# =============================================================================
#region ENTRY POINT
# =============================================================================
if __name__ == "__main__":
    main()
# endregion
# =============================================================================
