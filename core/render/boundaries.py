import pygame

# =====================================================================
#region BOUNDARIES RENDERER (LIMITES DEL NIVEL)
# Construye una superficie con los límites: techo, suelo y paredes
# =====================================================================
class BoundariesRenderer:

    # --------------------------------------------------------------
    #region INIT
    # Constructor y construcción inicial de la superficie
    # --------------------------------------------------------------
    def __init__(self, level):
        self.level = level
        self.surface = None
        self.build_surface()
    #endregion
    # --------------------------------------------------------------


    # --------------------------------------------------------------
    #region SURFACE BUILDER
    # Construye toda la superficie de límites (tiles o fallback simple)
    # --------------------------------------------------------------
    def build_surface(self):
        """Construye la superficie completa de los límites del nivel."""
        
        surf = pygame.Surface((self.level.ANCHO, self.level.ALTO), flags=pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))   # Fondo transparente

        # Si no hay tiles cargados, se dibuja un fallback sencillo
        if not self.level.tiles:
            self._draw_simple_boundaries(surf)
        else:
            self._draw_tiled_boundaries(surf)
        
        self.surface = surf
    #endregion
    # --------------------------------------------------------------


    # --------------------------------------------------------------
    #region SIMPLE BOUNDARIES (FALLBACK RENDER)
    # Límites generados con rectángulos de colores
    # --------------------------------------------------------------
    def _draw_simple_boundaries(self, surf):
        """Dibuja límites simples cuando no hay tiles cargados."""

        # TECHO
        pygame.draw.rect(
            surf, (80,80,100),
            (
                self.level.left_wall,
                self.level.ceiling_y,
                self.level.ANCHO,
                self.level.tile_h
            )
        )

        # SUELO
        pygame.draw.rect(
            surf, (120,70,30),
            (
                self.level.left_wall,
                self.level.floor_y,
                self.level.ANCHO,
                self.level.ALTO - self.level.floor_y
            )
        )

        # PARED IZQUIERDA
        pygame.draw.rect(
            surf, (100,100,100),
            (
                self.level.left_wall,
                self.level.ceiling_y + self.level.tile_h,
                10,
                self.level.floor_y - self.level.ceiling_y - self.level.tile_h
            )
        )

        # PARED DERECHA
        pygame.draw.rect(
            surf, (100,100,100),
            (
                self.level.right_wall - 10,
                self.level.ceiling_y + self.level.tile_h,
                10,
                self.level.floor_y - self.level.ceiling_y - self.level.tile_h
            )
        )
    #endregion
    # --------------------------------------------------------------


    # --------------------------------------------------------------
    #region TILED BOUNDARIES (CON SPRITES)
    # Dibuja límites usando el spritesheet de tiles
    # --------------------------------------------------------------
    def _draw_tiled_boundaries(self, surf):
        """Dibuja límites utilizando tiles cargados desde spritesheet."""

        tiles_across = (self.level.ANCHO + self.level.tile_w - 1) // self.level.tile_w
        
        # ---------------------------
        # TECHO (fila de tiles)
        # ---------------------------
        for col in range(tiles_across):
            tx = col * self.level.tile_w
            ty = self.level.ceiling_y
            idx = min(self.level.ceiling_tile_idx, len(self.level.tiles)-1)
            surf.blit(self.level.tiles[idx], (tx, ty))

        # ---------------------------
        # SUELO (una o varias filas)
        # ---------------------------
        floor_tiles_high = (self.level.ALTO - self.level.floor_y + self.level.tile_h - 1) // self.level.tile_h
        
        for row in range(floor_tiles_high):
            for col in range(tiles_across):
                tx = col * self.level.tile_w
                ty = self.level.floor_y + row * self.level.tile_h
                idx = min(self.level.floor_tile_idx, len(self.level.tiles)-1)
                surf.blit(self.level.tiles[idx], (tx, ty))

        # ---------------------------
        # PAREDES VERTICALES
        # ---------------------------
        start_y = self.level.ceiling_y + self.level.tile_h
        tiles_high = (self.level.floor_y - start_y + self.level.tile_h - 1) // self.level.tile_h
        
        idx = min(self.level.wall_tile_idx, len(self.level.tiles)-1)

        for row in range(tiles_high):
            ty = start_y + row * self.level.tile_h
            surf.blit(self.level.tiles[idx], (self.level.left_wall, ty))
            surf.blit(self.level.tiles[idx], (self.level.right_wall - self.level.tile_w, ty))
    #endregion
    # --------------------------------------------------------------


    # --------------------------------------------------------------
    #region DRAW
    # Dibuja la superficie ya construida
    # --------------------------------------------------------------
    def draw(self, screen):
        """Dibuja los límites ya construidos en la pantalla."""
        if self.surface:
            screen.blit(self.surface, (0, 0))
    #endregion
    # --------------------------------------------------------------

#endregion
# FIN BoundariesRenderer
