import pygame
import os
from core.audio.audio_manager import AudioManager
from core.entities.bullet import Bullet
from core.utils.spritesheet import load_image, slice_spritesheet

# =============================================================================
#region CLASS: PLAYER  (Jugador principal)
# =============================================================================

class Player:

    # Sprites y sonidos compartidos
    _player_sprites = None
    _shoot_sound = None
    _damage_sound = None
    _assets_loaded = False

    # -------------------------------------------------------------------------
    # LOAD ASSETS (Sprites y sonidos del jugador)
    # -------------------------------------------------------------------------
    @classmethod
    def load_assets(cls):
        """Carga sprites y sonidos del jugador una sola vez."""
        if cls._assets_loaded:
            return True
            
        # -------------------------
        # SPRITES DEL MAGO
        # -------------------------
        try:
            mage_sheet = load_image("assets/sprites/wizard.png")
            all_frames = slice_spritesheet(mage_sheet, 32, 32, spacing=0)

            cls._idle_sprites  = all_frames[0:5]
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
            fallback = pygame.Surface((32, 32))
            fallback.fill((150, 0, 255))
            pygame.draw.circle(fallback, (255, 200, 0), (16, 12), 8)

            cls._idle_sprites = cls._cast1_sprites = cls._cast2_sprites = cls._death_sprites = [fallback]
            cls._player_sprites = [fallback]

        # -------------------------
        # SONIDO: DISPARO
        # -------------------------
        try:
            if os.path.exists("assets/sounds/explosion_disparo.wav"):
                cls._shoot_sound = pygame.mixer.Sound("assets/sounds/explosion_disparo.wav")
                cls._shoot_sound.set_volume(AudioManager.sfx_volume)
            else:
                print("Advertencia: No se encontró explosion_disparo.wav")
                cls._shoot_sound = False
        except Exception as e:
            print(f"Error cargando sonido de disparo: {e}")
            cls._shoot_sound = False

        # -------------------------
        # SONIDO: DAÑO
        # -------------------------
        try:
            if os.path.exists("assets/sounds/hit01.wav"):
                cls._damage_sound = pygame.mixer.Sound("assets/sounds/hit01.wav")
                cls._damage_sound.set_volume(AudioManager.sfx_volume)
            else:
                print("Advertencia: No se encontró hit01.wav")
                cls._damage_sound = False
        except Exception as e:
            print(f"Error cargando sonido de daño: {e}")
            cls._damage_sound = False

        cls._assets_loaded = True
        return True

    # -------------------------------------------------------------------------
    # INIT
    # -------------------------------------------------------------------------
    def __init__(self, x, y):

        if not Player._assets_loaded:
            Player.load_assets()

        self.x = x
        self.y = y

        self.sprites = Player._idle_sprites
        self.current_sprite = 0
        self.width = self.sprites[0].get_width()
        self.height = self.sprites[0].get_height()

        # Movilidad
        self.speed = 6
        self.cooldown = 450
        self.ultimo_disparo = 0

        # Animación
        self.animation_speed = 6
        self.animation_counter = 0
        self.moving = False

        # Estados
        self.state = "idle"
        self.casting_animation_time = 0
        self.CASTING_DURATION = 300
        self.death_animation_started = False
        self.death_animation_finished = False

        # Vidas
        self.lives = 3
        self.invulnerable = False
        self.invulnerable_until = 0
        self.INVULNERABILITY_MS = 1500

    # -------------------------------------------------------------------------
    # MOVIMIENTO
    # -------------------------------------------------------------------------
    def mover(self, keys, limite_x):

        if self.lives <= 0:
            return
            
        self.moving = False
        
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
            self.moving = True
        if keys[pygame.K_RIGHT]:
            self.x += self.speed
            self.moving = True

        if self.x < 0:
            self.x = 0
        if self.x + self.width > limite_x:
            self.x = limite_x - self.width

    # -------------------------------------------------------------------------
    # ANIMACIÓN
    # -------------------------------------------------------------------------
    def update_animation(self):
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
        
        # Idle/movimiento
        if len(self.sprites) > 1 and not self.death_animation_finished:
            self.animation_counter += 1
            if self.animation_counter >= self.animation_speed:
                self.animation_counter = 0
                self.current_sprite = (self.current_sprite + 1) % len(self.sprites)

    # -------------------------------------------------------------------------
    # DISPARO
    # -------------------------------------------------------------------------
    def puede_disparar(self):
        return (pygame.time.get_ticks() - self.ultimo_disparo) >= self.cooldown

    def disparar(self, bala_sprite=None):

        if self.lives <= 0:
            return None
            
        if self.puede_disparar():

            self.ultimo_disparo = pygame.time.get_ticks()

            # Animación
            self.state = "casting"
            self.casting_animation_time = pygame.time.get_ticks() + self.CASTING_DURATION
            self.current_sprite = 0
            
            # Sonido → Actualizar volumen por si el usuario lo cambió
            if Player._shoot_sound:
                Player._shoot_sound.set_volume(AudioManager.sfx_volume)
                Player._shoot_sound.play()
            
            # Crear bala
            bullet_sprites = Bullet.get_bullet_sprites() if bala_sprite is None else (
                bala_sprite if isinstance(bala_sprite, list) else [bala_sprite]
            )
            
            bx = self.x + self.width // 2 - bullet_sprites[0].get_width() // 2
            by = self.y
            
            return Bullet(bx, by, bullet_sprites)

        return None

    # -------------------------------------------------------------------------
    # DAÑO
    # -------------------------------------------------------------------------
    def take_damage(self):

        if not self.invulnerable:

            self.lives -= 1
            self.invulnerable = True
            self.invulnerable_until = pygame.time.get_ticks() + self.INVULNERABILITY_MS
            
            # Sonido → Actualizar volumen según menú
            if Player._damage_sound:
                Player._damage_sound.set_volume(AudioManager.sfx_volume)
                Player._damage_sound.play()
                
            return True

        return False

    def update_invulnerability(self):
        if self.invulnerable and pygame.time.get_ticks() > self.invulnerable_until:
            self.invulnerable = False

    # -------------------------------------------------------------------------
    # ESTADO DE VIDA
    # -------------------------------------------------------------------------
    def is_dead(self):
        return self.lives <= 0 and self.death_animation_finished

    def is_dying(self):
        return self.lives <= 0 and self.death_animation_started and not self.death_animation_finished

    def is_alive(self):
        return self.lives > 0 and not self.is_dying()

    # -------------------------------------------------------------------------
    # DRAW
    # -------------------------------------------------------------------------
    def dibujar(self, pantalla):

        current_sprite = self.sprites[self.current_sprite]

        if self.invulnerable:
            if (pygame.time.get_ticks() // 150) % 2 == 0:
                pantalla.blit(current_sprite, (self.x, self.y))
        else:
            pantalla.blit(current_sprite, (self.x, self.y))

    # -------------------------------------------------------------------------
    # RESET
    # -------------------------------------------------------------------------
    def reset(self):

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

#endregion
# =============================================================================
