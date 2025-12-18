import pygame
from core.physics.collisions import CollisionSystem
from core.render.boundaries import BoundariesRenderer
from core.physics.platforms import AdvancedPlatformSystem


class BaseLevel:

        

    # region INIT & ESTADO GENERAL
    def __init__(self, pantalla, ANCHO, ALTO):
        self.pantalla = pantalla
        self.ANCHO = ANCHO
        self.ALTO = ALTO
        
        # Sistemas
        self.collision_system = CollisionSystem()
        self.boundaries_renderer = None
        self.platform_system = AdvancedPlatformSystem()
        
        # Estado del juego
        self.game_over = False
        self.level_won = False
        self.score = 0
        self.time_remaining = 99
        self.last_time_update = pygame.time.get_ticks()
        
        # Entidades
        self.player = None
        self.balls = []
        self.bullets = []
        
        # Assets
        self.background = None
        self.tiles = []
    # endregion


    # region LIMITES / BOUNDARIES
    def setup_level_boundaries(self, hud_height=50, floor_offset=48):
        """Configura los límites físicos del nivel"""
        self.hud_height = hud_height
        self.game_area_y_start = hud_height

        self.left_wall = 0
        self.right_wall = self.ANCHO
        self.ceiling_y = self.game_area_y_start
        self.floor_y = self.ALTO - floor_offset
        
        self.playfield_top = self.ceiling_y + 16
        self.playfield_bottom = self.floor_y
        self.playfield_left = self.left_wall + 16
        self.playfield_right = self.right_wall - 16
    # endregion


    # region ABSTRACT METHODS
    def load_assets(self): raise NotImplementedError
    def setup_player(self): raise NotImplementedError
    def spawn_initial_entities(self): raise NotImplementedError
    # endregion


    # region EVENTOS
    def handle_events(self, events):
        """Maneja input del usuario"""
        for event in events:
            if event.type == pygame.KEYDOWN:

                # Salir si WIN o GAME OVER
                if event.key == pygame.K_ESCAPE and (self.game_over or self.level_won):
                    return False

                # Reiniciar si WIN o GAME OVER
                if event.key == pygame.K_r and (self.game_over or self.level_won):
                    self.restart()
                    return True

                # Disparo
                if event.key == pygame.K_SPACE and not self.game_over and not self.level_won:
                    if self.player and self.player.is_alive():
                        new_bullet = self.player.disparar(None)
                        if new_bullet:
                            self.bullets.append(new_bullet)

        # Movimiento del jugador
        if (not self.game_over and not self.level_won 
            and self.player and self.player.is_alive()):
            keys = pygame.key.get_pressed()
            self.player.mover(keys, self.ANCHO)

        return True
    # endregion


    # region UPDATE LOOP
    def update(self, dt):
        """Actualiza el estado del nivel"""
        if self.game_over or self.level_won:
            return

        self._update_time()
        self._update_player()
        self._update_bullets()
        self._update_balls()
        self._update_platforms()
        self._process_collisions()

        # WIN CONDITION
        if len(self.balls) == 0:
            self.level_won = True
    # endregion


    # region SUB-UPDATES
    def _update_time(self):
        now = pygame.time.get_ticks()
        if now - self.last_time_update >= 1000:
            self.time_remaining -= 1
            self.last_time_update = now
            if self.time_remaining <= 0:
                self.time_remaining = 0
                self.game_over = True

    def _update_player(self):
        if self.player:
            self.player.update_invulnerability()
            self.player.update_animation()
            if self.player.lives <= 0 and self.player.is_dead():
                self.game_over = True

    def _update_bullets(self):
        for bullet in self.bullets[:]:
            bullet.actualizar()
            if not bullet.activa:
                self.bullets.remove(bullet)

    def _update_balls(self):
        if not self.game_over:
            for ball in self.balls[:]:
                ball.update(
                    self.floor_y,
                    self.playfield_left,
                    self.playfield_right,
                    self.game_area_y_start
                )

    def _process_collisions(self):
        if self.player and self.player.is_alive():
            self.collision_system.process_collisions(self)
    # endregion


    # region RENDER
    def draw(self):
        self._draw_background()
        self._draw_boundaries()
        self._draw_entities()
        self._draw_platforms()

    def _draw_background(self):
        if self.background:
            self.pantalla.blit(self.background, (0, 0))
        else:
            self.pantalla.fill((18, 18, 30))

    def _draw_boundaries(self):
        if self.boundaries_renderer:
            self.boundaries_renderer.draw(self.pantalla)

    def _draw_platforms(self):
        self.platform_system.draw(self.pantalla)

    def _draw_entities(self):
        # Bolas
        if not self.game_over:
            for ball in self.balls:
                ball.draw(self.pantalla)

        # Balas
        for bullet in self.bullets:
            bullet.dibujar(self.pantalla)

        # Jugador
        if self.player:
            self.player.dibujar(self.pantalla)
    # endregion


    # region RESTART / REINICIO
    def restart(self):
        """Reinicia el nivel desde cero"""
        self.game_over = False
        self.level_won = False      # RESET VICTORIA
        self.score = 0
        self.time_remaining = 99
        self.last_time_update = pygame.time.get_ticks()
        
        if self.player:
            self.player.reset()

        self.bullets.clear()
        self.balls.clear()

        self.spawn_initial_entities()
    # endregion

    #Esto  estaba dando error, pero asi se arreglo xd
    
    # region PLATFORM HELPERS (ADD PLATFORM)
    def add_platform(self, x, y, width, height, platform_type="normal"):
        """Agrega una plataforma normal"""
        return self.platform_system.add_platform(x, y, width, height, platform_type)

    def add_centered_platform(self, cx, cy, width, height, platform_type="normal"):
        """Agrega una plataforma centrada según su punto medio"""
        return self.platform_system.add_centered_platform(cx, cy, width, height, platform_type)
    # endregion

    # region UPDATE PLATFORMS
    def _update_platforms(self):
        """Actualiza colisiones de las plataformas con las bolas"""
        if not self.game_over and not self.level_won:
            for ball in self.balls[:]:
                self.platform_system.process_ball_collisions(ball)
    # endregion

