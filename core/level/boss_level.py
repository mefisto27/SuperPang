import pygame
from core.level.level1 import Level1
from core.entities.ball import Ball
from core.utils.spritesheet import load_image
import math


# =============================================================================
# CLASS: Boss (Jefe Final)
# =============================================================================
class Boss:

    def __init__(self, x, y):
        self.image = load_image("assets/sprites/boss_ice.png")
        self.image = pygame.transform.scale(self.image, (160, 120))

        self.x = x
        self.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        # Movimiento horizontal corto
        self.speed = 2
        self.direction = 1
        self.min_x = x - 60
        self.max_x = x + 26 + self.width

        # Vida
        self.max_hp = 15
        self.hp = self.max_hp

        # Disparo de bolas
        self.shoot_cooldown = 11000  # 11 segundos
        self.first_shot_delay = 500  # medio segundo
        self.first_shot_done = False
        self.spawn_time = pygame.time.get_ticks()
        self.last_shot = self.spawn_time

    def update(self):
        next_x = self.x + self.speed * self.direction

        if next_x <= self.min_x or next_x + self.width >= self.max_x:
            self.direction *= -1
        else:
            self.x = next_x

    def can_shoot(self):
        now = pygame.time.get_ticks()

        # Primer disparo a los 2 segundos
        if not self.first_shot_done:
            return now - self.spawn_time >= self.first_shot_delay

        # Disparos normales cada 20 segundos
        return now - self.last_shot >= self.shoot_cooldown

    def shoot_balls(self, custom_sprites):
        self.last_shot = pygame.time.get_ticks()
        self.first_shot_done = True

        balls = []
        cx = self.x + self.width // 2
        cy = self.y + self.height

        balls.append(Ball(cx - 40, cy, "big", 3, -8, custom_sprites=custom_sprites))
        balls.append(Ball(cx, cy, "big", -3, -8, custom_sprites=custom_sprites))
        balls.append(Ball(cx + 40, cy, "big", 2, -8, custom_sprites=custom_sprites))

        return balls

        balls = []
        cx = self.x + self.width // 2
        cy = self.y + self.height

        balls.append(Ball(cx - 40, cy, "big", 3, -8))
        balls.append(Ball(cx, cy, "big", -3, -8))
        balls.append(Ball(cx + 40, cy, "big", 2, -8))

        return balls

    def take_damage(self):
        self.hp -= 1

    def is_dead(self):
        return self.hp <= 0

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

        # Barra de vida
        bar_width = self.width
        hp_ratio = self.hp / self.max_hp

        pygame.draw.rect(
            screen, (120, 0, 0),
            (self.x, self.y - 12, bar_width, 8)
        )
        pygame.draw.rect(
            screen, (0, 200, 0),
            (self.x, self.y - 12, bar_width * hp_ratio, 8)
        )


# =============================================================================
# CLASS: IceCrystal (Cristal de Hielo)
# =============================================================================
class IceCrystal:

    def __init__(self, x, y):
        self.image = load_image("assets/sprites/ice_crystal.png")
        original_width = self.image.get_width()
        original_height = self.image.get_height()

        desired_height = 56  # ajusta este valor
        scale_ratio = desired_height / original_height
        new_width = int(original_width * scale_ratio)

        self.image = pygame.transform.scale(
            self.image,
            (new_width, desired_height)
        )

        self.x = x
        self.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        # Movimiento flotante suave
        self.base_y = y
        self.float_amplitude = 4
        self.float_speed = 0.003
        self.spawn_time = pygame.time.get_ticks()

        self.active = True

    def update(self):
        # Movimiento flotante (sube y baja)
        t = pygame.time.get_ticks() - self.spawn_time
        self.y = self.base_y + math.sin(t * self.float_speed) * self.float_amplitude

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


# =============================================================================
# CLASS: BossLevel
# =============================================================================
class BossLevel(Level1):

    def __init__(self, pantalla, ANCHO, ALTO):
        super().__init__(pantalla, ANCHO, ALTO)
        self.boss = None

        # Cristal de hielo
        self.ice_crystal = None
        self.crystal_spawn_delay = 3000  # segundos
        self.last_crystal_time = pygame.time.get_ticks()
        # Posiciones relativas del cristal (respecto al boss)
        self.crystal_positions = [
            (self.ANCHO - 130, 40),
            (220, 40),
            (self.ANCHO - 270, 40)
        ]
        self.crystal_pos_index = 0

    # -------------------------------------------------------------------------
    # LOAD ASSETS
    # -------------------------------------------------------------------------
    def load_assets(self):
        self._load_background()
        super().load_assets()  # crea plataformas, jugador, límites, etc.
        self._load_music()

    def _spawn_ice_crystal(self):
        x, y = self.crystal_positions[self.crystal_pos_index]
        y += self.game_area_y_start
        self.ice_crystal = IceCrystal(x, y)
        self.last_crystal_time = pygame.time.get_ticks()

    def _respawn_crystal_next_position(self):
        self.crystal_pos_index = (self.crystal_pos_index + 1) % len(self.crystal_positions)
        self._spawn_ice_crystal()

    def _check_crystal_collisions(self):
        if not self.ice_crystal:
            return

        crystal_rect = self.ice_crystal.get_rect()

        for bullet in self.bullets[:]:
            bullet_rect = pygame.Rect(
                bullet.x, bullet.y, bullet.width, bullet.height
            )

            if bullet_rect.colliderect(crystal_rect):
                self.bullets.remove(bullet)

                # Daño directo al boss
                self.boss.take_damage()
                self.boss.take_damage()  # 2 de daño total

                self.ice_crystal = None
                self._respawn_crystal_next_position()
                break

    def _load_background(self):
        try:
            bg = load_image("assets/boss_background.jpg")
            game_area_height = self.ALTO - self.game_area_y_start
            bg = pygame.transform.scale(bg, (self.ANCHO, game_area_height))

            self.background = pygame.Surface((self.ANCHO, self.ALTO))
            self.background.fill((18, 18, 30))
            self.background.blit(bg, (0, self.game_area_y_start))
        except:
            self.background = None

    def _load_music(self):
        try:
            pygame.mixer.music.load("assets/sounds/boss_theme.mp3")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print("Error música boss:", e)

    def _get_boss_ball_sprites(self):
        return {
            "big": "assets/sprites/boss_ball_big.png",
            "medium": "assets/sprites/boss_ball_medium.png",
            "small": "assets/sprites/boss_ball_small.png",
        }

    # -------------------------------------------------------------------------
    # ENTIDADES INICIALES
    # -------------------------------------------------------------------------
    def spawn_initial_entities(self):
        self.balls = []

        boss_x = self.ANCHO // 2 - 70
        boss_y = self.game_area_y_start + 40
        self.boss = Boss(boss_x, boss_y)

    # -------------------------------------------------------------------------
    # UPDATE
    # -------------------------------------------------------------------------
    def update(self, dt):
        if self.game_over or self.level_won:
            return

        # ======== lógica base SIN condición de victoria ========
        self._update_time()
        self._update_player()
        self._update_bullets()
        self._update_balls()
        self._update_platforms()
        self._process_collisions()

        # ======== lógica del boss ========
        self.boss.update()

        if self.boss.can_shoot():
            boss_sprites = self._get_boss_ball_sprites()
            self.balls.extend(self.boss.shoot_balls(boss_sprites))

        self._check_boss_collisions()

        # ======== CONDICIÓN DE VICTORIA REAL ========
        if self.boss.is_dead():
            self.level_won = True

        # ======== cristal de hielo ========
        now = pygame.time.get_ticks()

        if self.ice_crystal is None:
            if now - self.last_crystal_time >= self.crystal_spawn_delay:
                self._spawn_ice_crystal()
        else:
            self.ice_crystal.update()

    # -------------------------------------------------------------------------
    # COLISIONES BALA → BOSS
    # -------------------------------------------------------------------------
    def _check_boss_collisions(self):
        self._check_crystal_collisions()
        for bullet in self.bullets[:]:
            bullet_rect = pygame.Rect(
                bullet.x, bullet.y, bullet.width, bullet.height
            )
            boss_rect = pygame.Rect(
                self.boss.x, self.boss.y,
                self.boss.width, self.boss.height
            )

            if bullet_rect.colliderect(boss_rect):
                self.bullets.remove(bullet)
                self.boss.take_damage()
                self.score += 100

    # -------------------------------------------------------------------------
    # DRAW
    # -------------------------------------------------------------------------
    def draw(self):
        super().draw()

        if self.boss and not self.boss.is_dead():
            self.boss.draw(self.pantalla)

        if self.ice_crystal:
            self.ice_crystal.draw(self.pantalla)

    def detener_musica(self):
        pygame.mixer.music.stop()
