import pygame
import os
from core.entities.bullet import Bullet
from core.utils.spritesheet import load_image, slice_spritesheet


# =============================================================================
#region CLASS: PLAYER  (Jugador principal)
# =============================================================================

class Player:

    # -------------------------------------------------------------------------
    # region STATIC ASSETS (Sprites y sonidos compartidos)
    # -------------------------------------------------------------------------
    _player_sprites = None
    _shoot_sound = None
    _damage_sound = None
    _assets_loaded = False
    # endregion
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # region LOAD ASSETS (Sprites y sonidos del jugador)
    # -------------------------------------------------------------------------
    @classmethod
    def load_assets(cls):
        """Carga sprites y sonidos del jugador una sola vez."""
        if cls._assets_loaded:
            return True
            
        try:
            # Spritesheet del mago (160x128 → 5x4 frames)
            mage_sheet = load_image("assets/sprites/wizard.png")

            # Extraer todos los sprites 32x32
            all_frames = slice_spritesheet(mage_sheet, 32, 32, spacing=0)

            # Distribución de animaciones (5 frames por fila)
            cls._idle_sprites = all_frames[0:5]
            cls._cast1_sprites = all_frames[5:10]
            cls._cast2_sprites = all_frames[10:15]
            cls._death_sprites = all_frames[15:20]

            cls._player_sprites = cls._idle_sprites

            print(f"Mago cargado: {len(cls._idle_sprites)} idle, "
                  f"{len(cls._cast1_sprites)} cast1, "
                  f"{len(cls._cast2_sprites)} cast2, "
                  f"{len(cls._death_sprites)} death")

        except Exception as e:
            print(f"Error cargando spritesheet del mago: {e}")

            # Fallback para evitar crash
            fallback = pygame.Surface((32, 32))
            fallback.fill((150, 0, 255))
            pygame.draw.circle(fallback, (255, 200, 0), (16, 12), 8)

            cls._player_sprites = [fallback]
            cls._idle_sprites = cls._player_sprites
            cls._cast1_sprites = cls._player_sprites
            cls._cast2_sprites = cls._player_sprites
            cls._death_sprites = cls._player_sprites

        # Sonido de disparo
        try:
            if os.path.exists("assets/sounds/explosion_disparo.wav"):
                cls._shoot_sound = pygame.mixer.Sound("assets/sounds/explosion_disparo.wav")
            else:
                print("Advertencia: No se encontró explosion_disparo.wav")
                cls._shoot_sound = False
        except Exception as e:
            print(f"Error cargando sonido de disparo: {e}")
            cls._shoot_sound = False

        # Sonido de daño
        try:
            if os.path.exists("assets/sounds/hit01.wav"):
                cls._damage_sound = pygame.mixer.Sound("assets/sounds/hit01.wav")
            else:
                print("Advertencia: No se encontró damage.wav")
                cls._damage_sound = False
        except Exception as e:
            print(f"Error cargando sonido de daño: {e}")
            cls._damage_sound = False

        cls._assets_loaded = True
        return True
    # endregion
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # region INIT (Constructor del jugador)
    # -------------------------------------------------------------------------
    def __init__(self, x, y):

        if not Player._assets_loaded:
            Player.load_assets()

        # Posición inicial
        self.x = x
        self.y = y

        # Sprite actual (idle por defecto)
        self.sprites = Player._idle_sprites
        self.current_sprite = 0
        self.width = self.sprites[0].get_width()
        self.height = self.sprites[0].get_height()

        # Movimiento y disparo
        self.speed = 6
        self.cooldown = 450
        self.ultimo_disparo = 0

        # Animación
        self.animation_speed = 6
        self.animation_counter = 0
        self.moving = False

        # Estados de animación
        self.state = "idle"
        self.casting_animation_time = 0
        self.CASTING_DURATION = 300
        self.death_animation_started = False
        self.death_animation_finished = False

        # Vidas e invulnerabilidad
        self.lives = 3
        self.invulnerable = False
        self.invulnerable_until = 0
        self.INVULNERABILITY_MS = 1500
    # endregion
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # region MOVIMIENTO
    # -------------------------------------------------------------------------
    def mover(self, keys, limite_x):
        """Mueve al jugador dentro de los límites horizontales."""
        if self.lives <= 0:
            return
            
        self.moving = False
        
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
            self.moving = True
        if keys[pygame.K_RIGHT]:
            self.x += self.speed
            self.moving = True

        # Limitar a bordes del escenario
        if self.x < 0:
            self.x = 0
        if self.x + self.width > limite_x:
            self.x = limite_x - self.width
    # endregion
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # region ANIMATION HANDLING
    # -------------------------------------------------------------------------
    def update_animation(self):
        """Gestión de animaciones: idle, casting, death, etc."""
        current_time = pygame.time.get_ticks()
        
        # Muerte
        if self.lives <= 0 and not self.death_animation_finished:
            if not self.death_animation_started:
                self.state = "death"
                self.sprites = Player._death_sprites
                self.current_sprite = 0
                self.death_animation_started = True
                self.animation_counter = 0
            
            self.animation_counter += 1
            if self.animation_counter >= self.animation_speed * 2:
                self.animation_counter = 0
                if self.current_sprite < len(self.sprites) - 1:
                    self.current_sprite += 1
                else:
                    self.death_animation_finished = True
            return
        
        # Casting (disparo)
        if self.state == "casting" and self.lives > 0:
            if current_time < self.casting_animation_time:
                self.sprites = Player._cast1_sprites
            else:
                self.state = "idle"
                self.sprites = Player._idle_sprites
        
        # Idle o movimiento
        if len(self.sprites) > 1 and not self.death_animation_finished:
            self.animation_counter += 1
            if self.animation_counter >= self.animation_speed:
                self.animation_counter = 0
                self.current_sprite = (self.current_sprite + 1) % len(self.sprites)
    # endregion
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # region DISPARO
    # -------------------------------------------------------------------------
    def puede_disparar(self):
        """Retorna True si ya pasó el cooldown de disparo."""
        ahora = pygame.time.get_ticks()
        return (ahora - self.ultimo_disparo) >= self.cooldown

    def disparar(self, bala_sprite=None):
        """Genera y retorna una bala si el jugador puede disparar."""
        if self.lives <= 0:
            return None
            
        if self.puede_disparar():
            self.ultimo_disparo = pygame.time.get_ticks()

            # Animación de disparo
            self.state = "casting"
            self.casting_animation_time = pygame.time.get_ticks() + self.CASTING_DURATION
            self.current_sprite = 0
            
            if Player._shoot_sound:
                Player._shoot_sound.play()
            
            if bala_sprite is None:
                bullet_sprites = Bullet.get_bullet_sprites()
            else:
                bullet_sprites = bala_sprite if isinstance(bala_sprite, list) else [bala_sprite]
            
            bx = self.x + self.width // 2 - bullet_sprites[0].get_width() // 2
            by = self.y
            
            return Bullet(bx, by, bullet_sprites)

        return None
    # endregion
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # region DAMAGE / INVULNERABILITY
    # -------------------------------------------------------------------------
    def take_damage(self):
        """Aplica daño, reduce vidas y activa invulnerabilidad temporal."""
        if not self.invulnerable:
            self.lives -= 1
            self.invulnerable = True
            self.invulnerable_until = pygame.time.get_ticks() + self.INVULNERABILITY_MS
            
            if Player._damage_sound:
                Player._damage_sound.play()
                
            return True
        return False

    def update_invulnerability(self):
        """Actualiza estado de invulnerabilidad."""
        if self.invulnerable and pygame.time.get_ticks() > self.invulnerable_until:
            self.invulnerable = False
    # endregion
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # region LIFE STATE CHECKERS
    # -------------------------------------------------------------------------
    def is_dead(self):
        """True si la animación de muerte ya terminó."""
        return self.lives <= 0 and self.death_animation_finished

    def is_dying(self):
        """True si está en proceso de morir."""
        return self.lives <= 0 and self.death_animation_started and not self.death_animation_finished

    def is_alive(self):
        """True si sigue vivo y no está muriendo."""
        return self.lives > 0 and not self.is_dying()
    # endregion
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # region DRAW
    # -------------------------------------------------------------------------
    def dibujar(self, pantalla):
        """
        Dibuja el sprite actual. Si está invulnerable, parpadea.
        """

        current_sprite = self.sprites[self.current_sprite]

        if self.invulnerable:
            if (pygame.time.get_ticks() // 150) % 2 == 0:
                pantalla.blit(current_sprite, (self.x, self.y))
        else:
            pantalla.blit(current_sprite, (self.x, self.y))

        # Código duplicado original (se mantiene intacto para no alterar lógica)
        current_sprite = self.sprites[self.current_sprite]
        if self.invulnerable:
            if (pygame.time.get_ticks() // 150) % 2 == 0:
                pantalla.blit(current_sprite, (self.x, self.y))
        else:
            pantalla.blit(current_sprite, (self.x, self.y))
    # endregion
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # region RESET
    # -------------------------------------------------------------------------
    def reset(self):
        """Reinicia el estado completo del jugador."""
        self.lives = 3
        self.invulnerable = False
        self.invulnerable_until = 0
        self.state = "idle"
        self.death_animation_started = False
        self.death_animation_finished = False
        self.sprites = Player._idle_sprites
        self.current_sprite = 0
        self.animation_counter = 0
        self.moving = False
        self.casting_animation_time = 0
    # endregion
    # -------------------------------------------------------------------------

#endregion
# =============================================================================
