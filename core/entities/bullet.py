import pygame
from core.utils.spritesheet import load_image, slice_spritesheet


# =============================================================================
#region CLASS: BULLET (Bala del jugador)
# =============================================================================

class Bullet:

    # -------------------------------------------------------------------------
    # region STATIC ASSETS (Sprites globales de la bala)
    # -------------------------------------------------------------------------
    _bullet_sprites = None
    _assets_loaded = False
    # endregion
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # region LOAD ASSETS (Carga spritesheet y los 64 frames)
    # -------------------------------------------------------------------------
    @classmethod
    def load_assets(cls):
        """Carga todos los frames de animación de la bala una sola vez."""
        if cls._assets_loaded:
            return True
            
        try:
            # Spritesheet completo 800x800 (8x8 → 64 frames)
            bullet_sheet = load_image("assets/sprites/7_firespin_spritesheet.png")
            bullet_sheet = bullet_sheet.convert_alpha()
            
            frame_width = 100
            frame_height = 100
            
            print(f"Cargando animación completa: 64 frames de {frame_width}x{frame_height}")
            
            cls._bullet_sprites = []

            # Extraer los 64 frames (8 filas × 8 columnas)
            for row in range(8):
                for col in range(8):
                    x = col * frame_width
                    y = row * frame_height
                    
                    frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                    frame.blit(bullet_sheet, (0, 0), (x, y, frame_width, frame_height))
                    cls._bullet_sprites.append(frame)
            
            # Reescalar para que la bala no sea gigante
            scaled_frames = []
            target_size = 64  # Tamaño final de la bala
            
            for frame in cls._bullet_sprites:
                scaled_frame = pygame.transform.scale(frame, (target_size, target_size))
                scaled_frames.append(scaled_frame)
            
            cls._bullet_sprites = scaled_frames
            
            print(f"Bala: {len(cls._bullet_sprites)} frames de animación cargados ({target_size}x{target_size})")
            
        except Exception as e:
            print(f"Error cargando spritesheet de bala: {e}")

            # Fallback de emergencia: animación simple
            cls._bullet_sprites = []
            for i in range(16):
                surf = pygame.Surface((20, 20), pygame.SRCALPHA)
                intensity = 150 + (i % 4) * 25
                pygame.draw.circle(surf, (255, intensity, 0), (10, 10), 8)
                cls._bullet_sprites.append(surf)

        cls._assets_loaded = True
        return True
    # endregion
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # region GET ASSETS (Obtener sprites de bala)
    # -------------------------------------------------------------------------
    @classmethod
    def get_bullet_sprites(cls):
        """Retorna los sprites de la bala (cargándolos si es necesario)."""
        if not cls._assets_loaded:
            cls.load_assets()
        return cls._bullet_sprites
    # endregion
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # region INIT (Construcción de instancia de la bala disparada)
    # -------------------------------------------------------------------------
    def __init__(self, x, y, sprite_frames=None):
        """
        Crea una bala en (x, y), con los frames de animación especificados.
        Si no se pasan frames, utiliza los del spritesheet global.
        """
        # Hitbox lógico (NO depende del sprite)
        self.hitbox_width = 8
        self.hitbox_height = 12

        self.x = x
        self.y = y
        
        # Usar los sprites globales si no se proporcionan otros
        if sprite_frames is None:
            self.sprite_frames = Bullet.get_bullet_sprites()
        else:
            self.sprite_frames = sprite_frames if isinstance(sprite_frames, list) else [sprite_frames]

        self.width = self.sprite_frames[0].get_width()
        self.height = self.sprite_frames[0].get_height()
        
        # Movimiento
        self.vel = 10
        self.activa = True
        
        # Animación
        self.current_frame = 0
        self.animation_speed = 3
        self.animation_counter = 0
    # endregion
    # -------------------------------------------------------------------------


    def get_hitbox(self):
        """
        Retorna el rect de colisión REAL de la bala
        (punta superior, sin padding transparente)
        """
        hitbox_x = self.x + (self.width // 2) - (self.hitbox_width // 2)
        hitbox_y = self.y  # punta superior

        return pygame.Rect(
            hitbox_x,
            hitbox_y,
            self.hitbox_width,
            self.hitbox_height
        )

    # -------------------------------------------------------------------------
    # region UPDATE (Movimiento y animación)
    # -------------------------------------------------------------------------
    def actualizar(self):
        """Actualiza posición y animación de la bala."""
        
        # Movimiento vertical hacia arriba
        self.y -= self.vel
        
        # Animación
        if len(self.sprite_frames) > 1:
            self.animation_counter += 1
            if self.animation_counter >= self.animation_speed:
                self.animation_counter = 0
                self.current_frame = (self.current_frame + 1) % len(self.sprite_frames)
        
        # Desactivar si sale de pantalla
        if self.y + self.height < 0:
            self.activa = False
    # endregion
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # region DRAW (Dibujar bala)
    # -------------------------------------------------------------------------
    def dibujar(self, pantalla):
        """Dibuja la bala en pantalla usando su frame actual."""
        current_sprite = self.sprite_frames[self.current_frame]
        pantalla.blit(current_sprite, (self.x, self.y))
    # endregion
    # -------------------------------------------------------------------------

#endregion
# =============================================================================
