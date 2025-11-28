import pygame
import math
import os

# =============================================================================
#region CLASS: BALL (Bola de Super Pang)
# =============================================================================
class Ball:

    # -------------------------------------------------------------------------
    # region SPRITES Y PROPIEDADES ESTÁTICAS
    # -------------------------------------------------------------------------
    # Sprites por tamaño
    sprite_by_size = {
        "big": "assets/sprites/orb_red.png",
        "medium": "assets/sprites/orb_blue.png",
        "small": "assets/sprites/orb_purple.png"
    }

    # Factores de rebote por tamaño
    bounce_factor_by_size = {
        "big": 0.9,
        "medium": 0.85,
        "small": 0.8
    }

    # Parámetros físicos globales
    MIN_VY = 6                     # Velocidad mínima al rebotar
    MIN_BOUNCE_HEIGHT = 200        # Altura mínima solo para rebotes en piso

    # Sonido cargado bajo demanda
    _explode_sound = None
    # endregion
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # region LOAD SOUND (Lazy load del sonido de explosión)
    # -------------------------------------------------------------------------
    @classmethod
    def _get_explode_sound(cls):
        """Carga el sonido de explosión la primera vez que se requiera."""
        if cls._explode_sound is None:
            try:
                path = "assets/sounds/explosion_bola.wav"
                if os.path.exists(path):
                    cls._explode_sound = pygame.mixer.Sound(path)
                else:
                    print("Advertencia: No se encontró explosion_bola.wav")
                    cls._explode_sound = False
            except Exception as e:
                print("Error cargando sonido:", e)
                cls._explode_sound = False
        return cls._explode_sound
    # endregion
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # region INIT (Constructor)
    # -------------------------------------------------------------------------
    def __init__(self, x, y, size, vx, vy):
        """
        x, y: posición de la bola
        size: "big", "medium", "small"
        vx, vy: velocidad inicial
        """
        self.x = x
        self.y = y
        self.size = size
        self.vx = vx
        self.vy = vy

        # Física
        self.gravity = 0.18
        self.bounce_factor = self.bounce_factor_by_size[size]

        # Radios por tamaño
        self.radius_by_size = {
            "big": 40,
            "medium": 25,
            "small": 15
        }

        # Control de comportamiento de rebotes
        self.bounce_count = 0
        self.max_bounces_before_low = 3
        self.just_bounced = 0  # evita rebotes consecutivos en un mismo frame

        # ------------------------------------------------------
        # Cargar sprite correspondiente al tamaño
        # ------------------------------------------------------
        r = self.radius_by_size[self.size]
        try:
            img = pygame.image.load(self.sprite_by_size[self.size]).convert_alpha()
            self.image = pygame.transform.scale(img, (2*r, 2*r))
        except:
            # Fallback visual si hay error
            self.image = pygame.Surface((2*r, 2*r), pygame.SRCALPHA)
            color = {
                "big": (255,0,0),
                "medium": (0,0,255),
                "small": (128,0,128)
            }[size]
            pygame.draw.circle(self.image, color, (r, r), r)
    # endregion
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # region BOUNCE LOGIC (Lógica de rebote vertical)
    # -------------------------------------------------------------------------
    def bounce_vertical(self, use_min_height=True):
        """
        Rebote vertical con reglas diferenciadas para piso y plataformas.
        use_min_height:
            True  -> aplicar altura mínima (solo piso)
            False -> rebote normal (plataformas y techo)
        """
        # Rebote "fuerte" en piso después de varios rebotes
        if use_min_height and self.bounce_count > self.max_bounces_before_low:
            required_vy = -math.sqrt(2 * self.gravity * self.MIN_BOUNCE_HEIGHT)
            if self.vy > required_vy:
                self.vy = required_vy
        else:
            # Rebote normal
            self.vy = -abs(self.vy) * self.bounce_factor

        # Velocidades límite
        if abs(self.vy) < self.MIN_VY:
            self.vy = -self.MIN_VY
        if abs(self.vy) > 18:
            self.vy = -18

        self.just_bounced = 3  # anti-doble-rebote
    # endregion
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # region UPDATE (Física principal de la bola)
    # -------------------------------------------------------------------------
    def update(self, floor_y, left_wall, right_wall, ceiling_y):
        """
        Actualiza la física general de la bola y controla colisiones
        contra paredes, techo y piso.
        """
        r = self.radius_by_size[self.size]

        # Reducir cooldown anti-doble-bounce
        if self.just_bounced > 0:
            self.just_bounced -= 1

        # Aplicar gravedad y actualizar posición
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy

        # ============================================================
        #   TECHO
        # ============================================================
        ceiling_limit = ceiling_y + 16  # grosor de tile superior

        if self.y - r <= ceiling_limit:
            self.y = ceiling_limit + r

            if self.just_bounced == 0:
                self.vy = abs(self.vy) * self.bounce_factor  # rebote hacia abajo
                if self.vy < self.MIN_VY:
                    self.vy = self.MIN_VY
                self.just_bounced = 3

            return

        # ============================================================
        #   PISO
        # ============================================================
        if self.y + r >= floor_y and self.just_bounced == 0:
            self.y = floor_y - r
            self.bounce_count += 1
            self.bounce_vertical(use_min_height=True)
            self.y -= 1
            return

        # ============================================================
        #   PAREDES
        # ============================================================
        if self.x - r <= left_wall:
            self.x = left_wall + r
            self.vx = abs(self.vx) * self.bounce_factor

        if self.x + r >= right_wall:
            self.x = right_wall - r
            self.vx = -abs(self.vx) * self.bounce_factor
    # endregion
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # region SPLIT (División al ser golpeada)
    # -------------------------------------------------------------------------
    def split(self):
        """Divide la bola en dos más pequeñas, o desaparece si es small."""
        if self.size == "small":
            return []

        snd = self._get_explode_sound()
        if snd:
            snd.play()

        new_size = "medium" if self.size == "big" else "small"

        # Genera dos bolas con velocidades opuestas
        return [
            Ball(self.x, self.y, new_size, 3, -8),
            Ball(self.x, self.y, new_size, -3, -8)
        ]
    # endregion
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # region DRAW (Dibujar bola)
    # -------------------------------------------------------------------------
    def draw(self, screen):
        """Dibuja la bola considerando su radio."""
        r = self.radius_by_size[self.size]
        screen.blit(self.image, (self.x - r, self.y - r))
    # endregion
    # -------------------------------------------------------------------------

#endregion
# =============================================================================
